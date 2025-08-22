import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.services.task_service import TaskService
from app.schemas.task import SubTaskCreate, SubTaskUpdate
from app.core.exceptions import NotFoundError, ValidationError


class TestTaskService:
    """Test cases for TaskService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def task_service(self, mock_db):
        """Create TaskService instance with mock dependencies."""
        with patch('app.services.task_service.TaskRepository') as mock_task_repo, \
             patch('app.services.task_service.SubTaskRepository') as mock_subtask_repo, \
             patch('app.services.task_service.VariantRepository') as mock_variant_repo, \
             patch('app.services.task_service.SubjectRepository') as mock_subject_repo:
            
            service = TaskService(mock_db)
            service.task_repo = mock_task_repo.return_value
            service.subtask_repo = mock_subtask_repo.return_value
            service.variant_repo = mock_variant_repo.return_value
            service.subject_repo = mock_subject_repo.return_value
            
            yield service
    
    def test_get_subjects_success(self, task_service):
        """Test successful retrieval of subjects."""
        # Arrange
        mock_subjects = [
            Mock(ID=1, Name="Mathematics", Description="Math course"),
            Mock(ID=2, Name="Physics", Description="Physics course")
        ]
        task_service.subject_repo.get_all.return_value = mock_subjects
        
        # Act
        result = task_service.get_subjects()
        
        # Assert
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].name == "Mathematics"
        assert result[1].id == 2
        assert result[1].name == "Physics"
        task_service.subject_repo.get_all.assert_called_once_with(skip=0, limit=100)
    
    def test_get_subject_success(self, task_service):
        """Test successful retrieval of a single subject."""
        # Arrange
        mock_subject = Mock(ID=1, Name="Mathematics", Description="Math course")
        task_service.subject_repo.get_or_404.return_value = mock_subject
        
        # Act
        result = task_service.get_subject(1)
        
        # Assert
        assert result.id == 1
        assert result.name == "Mathematics"
        assert result.description == "Math course"
        task_service.subject_repo.get_or_404.assert_called_once_with(1)
    
    def test_get_subject_not_found(self, task_service):
        """Test subject retrieval when subject doesn't exist."""
        # Arrange
        task_service.subject_repo.get_or_404.side_effect = NotFoundError("Subject", "1")
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            task_service.get_subject(999)
    
    def test_get_tasks_with_subject_filter(self, task_service):
        """Test retrieval of tasks filtered by subject."""
        # Arrange
        mock_tasks = [
            Mock(
                TaskID=1, TaskNumber=1, TaskTitle="Algebra",
                SubjectID=1,
                subject=Mock(ID=1, Name="Mathematics", Description="Math course")
            )
        ]
        task_service.task_repo.get_tasks_by_subject.return_value = mock_tasks
        
        # Act
        result = task_service.get_tasks(subject_id=1)
        
        # Assert
        assert len(result) == 1
        assert result[0].task_id == 1
        assert result[0].task_title == "Algebra"
        assert result[0].subject_id == 1
        task_service.task_repo.get_tasks_by_subject.assert_called_once_with(1, skip=0, limit=100)
    
    def test_get_tasks_without_subject_filter(self, task_service):
        """Test retrieval of all tasks without subject filter."""
        # Arrange
        mock_tasks = [
            Mock(
                TaskID=1, TaskNumber=1, TaskTitle="Algebra",
                SubjectID=1,
                subject=Mock(ID=1, Name="Mathematics", Description="Math course")
            )
        ]
        task_service.task_repo.get_all.return_value = mock_tasks
        
        # Act
        result = task_service.get_tasks()
        
        # Assert
        assert len(result) == 1
        assert result[0].task_id == 1
        task_service.task_repo.get_all.assert_called_once_with(skip=0, limit=100)
    
    def test_create_subtask_success(self, task_service):
        """Test successful creation of a subtask."""
        # Arrange
        subtask_data = SubTaskCreate(
            task_id=1,
            subtask_number=1,
            description="Test subtask",
            answer="42"
        )
        
        mock_task = Mock(TaskID=1)
        mock_subtask = Mock(
            SubTaskID=1, TaskID=1, SubTaskNumber=1,
            Description="Test subtask", Answer="42",
            VariantID=None, variant=None,
            ImagePath=None, SolutionPath=None
        )
        
        task_service.task_repo.get_or_404.return_value = mock_task
        task_service.subtask_repo.create_subtask.return_value = mock_subtask
        
        # Act
        result = task_service.create_subtask(subtask_data)
        
        # Assert
        assert result.subtask_id == 1
        assert result.task_id == 1
        assert result.description == "Test subtask"
        assert result.answer == "42"
        task_service.task_repo.get_or_404.assert_called_once_with(1)
        task_service.subtask_repo.create_subtask.assert_called_once()
    
    def test_create_subtask_task_not_found(self, task_service):
        """Test subtask creation when task doesn't exist."""
        # Arrange
        subtask_data = SubTaskCreate(
            task_id=999,
            subtask_number=1,
            description="Test subtask",
            answer="42"
        )
        
        task_service.task_repo.get_or_404.side_effect = NotFoundError("Task", "999")
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            task_service.create_subtask(subtask_data)
    
    def test_check_answer_success(self, task_service):
        """Test successful answer checking."""
        # Arrange
        mock_subtask = Mock(
            SubTaskID=1,
            Answer="42"
        )
        task_service.subtask_repo.get_or_404.return_value = mock_subtask
        
        # Act
        result = task_service.check_answer(1, "42")
        
        # Assert
        assert result["subtask_id"] == 1
        assert result["student_answer"] == "42"
        assert result["correct_answer"] == "42"
        assert result["is_correct"] is True
        assert result["score"] == 1.0
    
    def test_check_answer_incorrect(self, task_service):
        """Test answer checking with incorrect answer."""
        # Arrange
        mock_subtask = Mock(
            SubTaskID=1,
            Answer="42"
        )
        task_service.subtask_repo.get_or_404.return_value = mock_subtask
        
        # Act
        result = task_service.check_answer(1, "43")
        
        # Assert
        assert result["is_correct"] is False
        assert result["score"] == 0.0
    
    def test_check_answer_no_answer_configured(self, task_service):
        """Test answer checking when subtask has no answer configured."""
        # Arrange
        mock_subtask = Mock(
            SubTaskID=1,
            Answer=None
        )
        task_service.subtask_repo.get_or_404.return_value = mock_subtask
        
        # Act & Assert
        with pytest.raises(ValidationError):
            task_service.check_answer(1, "42")
    
    def test_check_answer_case_insensitive(self, task_service):
        """Test that answer checking is case insensitive."""
        # Arrange
        mock_subtask = Mock(
            SubTaskID=1,
            Answer="ANSWER"
        )
        task_service.subtask_repo.get_or_404.return_value = mock_subtask
        
        # Act
        result = task_service.check_answer(1, "answer")
        
        # Assert
        assert result["is_correct"] is True
        assert result["score"] == 1.0
