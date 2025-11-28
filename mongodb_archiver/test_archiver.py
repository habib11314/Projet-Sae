"""
Unit tests for MongoDB Order Archiver
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from bson import ObjectId

from config import Config
from archiver import OrderArchiver
from watcher import OrderWatcher


@pytest.fixture
def mock_config():
    """Create a mock configuration"""
    return Config(
        mongodb_uri="mongodb://localhost:27017/",
        database_name="Test_DB",
        batch_size=10
    )


@pytest.fixture
def mock_logger():
    """Create a mock logger"""
    return Mock()


class TestOrderArchiver:
    """Tests for OrderArchiver class"""
    
    def test_config_creation(self):
        """Test config creation with different methods"""
        config = Config(mongodb_uri="mongodb://localhost:27017/")
        assert config.mongodb_uri == "mongodb://localhost:27017/"
        assert config.database_name == "Ubereats"
        assert config.batch_size == 100
    
    def test_config_simulation(self):
        """Test simulation config"""
        config = Config.for_simulation()
        assert "localhost" in config.mongodb_uri
        assert config.database_name == "Ubereats_Test"
    
    def test_archiver_initialization(self, mock_config, mock_logger):
        """Test archiver initialization"""
        archiver = OrderArchiver(mock_config, mock_logger)
        assert archiver.config == mock_config
        assert archiver.logger == mock_logger
        assert archiver.stats['found'] == 0
        assert archiver.stats['archived'] == 0
    
    def test_get_enrichment_pipeline(self, mock_config, mock_logger):
        """Test pipeline generation"""
        archiver = OrderArchiver(mock_config, mock_logger)
        pipeline = archiver.get_enrichment_pipeline("CMD-001")
        
        # Check pipeline structure
        assert isinstance(pipeline, list)
        assert len(pipeline) > 0
        assert pipeline[0]['$match']['numero_commande'] == "CMD-001"
        
        # Check that lookups are present
        lookup_stages = [stage for stage in pipeline if '$lookup' in stage]
        assert len(lookup_stages) == 4  # Client, Livreur, Restaurant, Menu
    
    def test_check_completeness_complete(self, mock_config, mock_logger):
        """Test completeness check with complete order"""
        archiver = OrderArchiver(mock_config, mock_logger)
        
        order = {
            'nom_client': 'Jean Dupont',
            'nom_livreur': 'Alice Martin',
            'nom_restaurant': 'Le Bistrot',
            'nom_menu': 'Menu du jour',
            'coût_commande': 15.5
        }
        
        is_complete, missing = archiver.check_completeness(order)
        assert is_complete is True
        assert len(missing) == 0
    
    def test_check_completeness_incomplete(self, mock_config, mock_logger):
        """Test completeness check with incomplete order"""
        archiver = OrderArchiver(mock_config, mock_logger)
        
        order = {
            'nom_client': 'Client inconnu',
            'nom_livreur': 'Alice Martin',
            'nom_restaurant': 'Restaurant non spécifié',
            'nom_menu': None,
            'coût_commande': 15.5
        }
        
        is_complete, missing = archiver.check_completeness(order)
        assert is_complete is False
        assert 'nom_client' in missing
        assert 'nom_restaurant' in missing
        assert 'nom_menu' in missing
    
    def test_stats_summary_format(self, mock_config, mock_logger):
        """Test statistics summary formatting"""
        archiver = OrderArchiver(mock_config, mock_logger)
        archiver.stats = {
            'found': 100,
            'archived': 95,
            'duplicates': 3,
            'incomplete': 10,
            'errors': 2
        }
        
        summary = archiver.get_stats_summary()
        assert 'Found:       100' in summary
        assert 'Archived:    95' in summary
        assert 'Duplicates:  3' in summary


class TestOrderWatcher:
    """Tests for OrderWatcher class"""
    
    def test_watcher_initialization(self, mock_config, mock_logger):
        """Test watcher initialization"""
        watcher = OrderWatcher(mock_config, mock_logger)
        assert watcher.config == mock_config
        assert watcher.archiver is not None
    
    def test_should_archive_insert_delivered(self, mock_config, mock_logger):
        """Test should_archive with insert of delivered order"""
        watcher = OrderWatcher(mock_config, mock_logger)
        
        change = {
            'operationType': 'insert',
            'fullDocument': {
                'numero_commande': 'CMD-001',
                'status': 'livrée'
            }
        }
        
        assert watcher.should_archive(change) is True
    
    def test_should_archive_update_to_delivered(self, mock_config, mock_logger):
        """Test should_archive when status changes to delivered"""
        watcher = OrderWatcher(mock_config, mock_logger)
        
        change = {
            'operationType': 'update',
            'fullDocument': {
                'numero_commande': 'CMD-001',
                'status': 'livrée'
            },
            'updateDescription': {
                'updatedFields': {
                    'status': 'livrée'
                }
            }
        }
        
        assert watcher.should_archive(change) is True
    
    def test_should_archive_other_status(self, mock_config, mock_logger):
        """Test should_archive with non-delivered status"""
        watcher = OrderWatcher(mock_config, mock_logger)
        
        change = {
            'operationType': 'insert',
            'fullDocument': {
                'numero_commande': 'CMD-001',
                'status': 'en_cours'
            }
        }
        
        assert watcher.should_archive(change) is False
    
    def test_should_archive_delete_operation(self, mock_config, mock_logger):
        """Test should_archive with delete operation"""
        watcher = OrderWatcher(mock_config, mock_logger)
        
        change = {
            'operationType': 'delete',
            'documentKey': {'_id': ObjectId()}
        }
        
        assert watcher.should_archive(change) is False


class TestIntegration:
    """Integration tests (require actual MongoDB connection)"""
    
    @pytest.mark.skip(reason="Requires MongoDB connection")
    def test_full_archive_flow(self):
        """Test complete archiving flow"""
        # This would test with a real MongoDB instance
        pass
    
    @pytest.mark.skip(reason="Requires MongoDB connection")
    def test_watch_flow(self):
        """Test watch mode flow"""
        # This would test with a real MongoDB instance
        pass


def test_config_from_env_missing():
    """Test config creation fails without MONGODB_URI"""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="MONGODB_URI"):
            Config.from_env()


def test_config_from_env_with_uri():
    """Test config creation with MONGODB_URI"""
    test_uri = "mongodb://testhost:27017/"
    with patch.dict('os.environ', {'MONGODB_URI': test_uri}):
        config = Config.from_env()
        assert config.mongodb_uri == test_uri


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
