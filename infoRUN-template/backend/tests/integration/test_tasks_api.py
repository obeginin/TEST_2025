import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.subject import Subject
from app.models.task import Task, SubTask
from app.core.security import get_password_hash


class TestTasksAPI:
    """Integration tests for tasks API endpoints."""
    
    def test_get_subjects_success(self, client: TestClient, db_session: Session, factory):
        """Test successful retrieval of subjects."""
        # Arrange
        subject1 = factory.create_subject(db_session, Name="Mathematics", Description="Math course")
        subject2 = factory.create_subject(db_session, Name="Physics", Description="Physics course")
        
        # Act
        response = client.get("/api/v1/tasks/subjects")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == "Mathematics"
        assert data["data"][1]["name"] == "Physics"
    
    def test_get_subjects_empty(self, client: TestClient, db_session: Session):
        """Test retrieval of subjects when none exist."""
        # Act
        response = client.get("/api/v1/tasks/subjects")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0
    
    def test_get_subject_success(self, client: TestClient, db_session: Session, factory):
        """Test successful retrieval of a single subject."""
        # Arrange
        subject = factory.create_subject(db_session, Name="Mathematics", Description="Math course")
        
        # Act
        response = client.get(f"/api/v1/tasks/subjects/{subject.ID}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == subject.ID
        assert data["data"]["name"] == "Mathematics"
        assert data["data"]["description"] == "Math course"
    
    def test_get_subject_not_found(self, client: TestClient, db_session: Session):
        """Test retrieval of non-existent subject."""
        # Act
        response = client.get("/api/v1/tasks/subjects/999")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_get_tasks_success(self, client: TestClient, db_session: Session, factory):
        """Test successful retrieval of tasks."""
        # Arrange
        subject = factory.create_subject(db_session, Name="Mathematics")
        task1 = factory.create_task(db_session, TaskNumber=1, TaskTitle="Algebra", SubjectID=subject.ID)
        task2 = factory.create_task(db_session, TaskNumber=2, TaskTitle="Calculus", SubjectID=subject.ID)
        
        # Act
        response = client.get("/api/v1/tasks")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["task_title"] == "Algebra"
        assert data["data"][1]["task_title"] == "Calculus"
    
    def test_get_tasks_by_subject(self, client: TestClient, db_session: Session, factory):
        """Test retrieval of tasks filtered by subject."""
        # Arrange
        subject1 = factory.create_subject(db_session, Name="Mathematics")
        subject2 = factory.create_subject(db_session, Name="Physics")
        
        task1 = factory.create_task(db_session, TaskNumber=1, TaskTitle="Algebra", SubjectID=subject1.ID)
        task2 = factory.create_task(db_session, TaskNumber=2, TaskTitle="Mechanics", SubjectID=subject2.ID)
        
        # Act
        response = client.get(f"/api/v1/tasks?subject_id={subject1.ID}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["task_title"] == "Algebra"
        assert data["data"][0]["subject_id"] == subject1.ID
    
    def test_get_task_success(self, client: TestClient, db_session: Session, factory):
        """Test successful retrieval of a single task."""
        # Arrange
        subject = factory.create_subject(db_session, Name="Mathematics")
        task = factory.create_task(db_session, TaskNumber=1, TaskTitle="Algebra", SubjectID=subject.ID)
        
        # Act
        response = client.get(f"/api/v1/tasks/{task.TaskID}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["task_id"] == task.TaskID
        assert data["data"]["task_title"] == "Algebra"
        assert data["data"]["subject_id"] == subject.ID
    
    def test_get_task_not_found(self, client: TestClient, db_session: Session):
        """Test retrieval of non-existent task."""
        # Act
        response = client.get("/api/v1/tasks/999")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_get_task_subtasks_success(self, client: TestClient, db_session: Session, factory):
        """Test successful retrieval of subtasks for a task."""
        # Arrange
        subject = factory.create_subject(db_session, Name="Mathematics")
        task = factory.create_task(db_session, TaskNumber=1, TaskTitle="Algebra", SubjectID=subject.ID)
        
        subtask1 = factory.create_subtask(db_session, TaskID=task.TaskID, SubTaskNumber=1, Description="Solve equation")
        subtask2 = factory.create_subtask(db_session, TaskID=task.TaskID, SubTaskNumber=2, Description="Graph function")
        
        # Act
        response = client.get(f"/api/v1/tasks/{task.TaskID}/subtasks")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["subtask_number"] == 1
        assert data["data"][1]["subtask_number"] == 2
    
    def test_get_task_subtasks_empty(self, client: TestClient, db_session: Session, factory):
        """Test retrieval of subtasks when task has none."""
        # Arrange
        subject = factory.create_subject(db_session, Name="Mathematics")
        task = factory.create_task(db_session, TaskNumber=1, TaskTitle="Algebra", SubjectID=subject.ID)
        
        # Act
        response = client.get(f"/api/v1/tasks/{task.TaskID}/subtasks")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0
    
    def test_get_variants_success(self, client: TestClient, db_session: Session, factory):
        """Test successful retrieval of variants."""
        # Arrange
        from app.models.task import Variant
        variant1 = Variant(VariantName="Variant A", Description="First variant")
        variant2 = Variant(VariantName="Variant B", Description="Second variant")
        
        db_session.add(variant1)
        db_session.add(variant2)
        db_session.commit()
        
        # Act
        response = client.get("/api/v1/tasks/variants")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["variant_name"] == "Variant A"
        assert data["data"][1]["variant_name"] == "Variant B"
    
    def test_check_answer_success(self, client: TestClient, db_session: Session, factory):
        """Test successful answer checking."""
        # Arrange
        subject = factory.create_subject(db_session, Name="Mathematics")
        task = factory.create_task(db_session, TaskNumber=1, TaskTitle="Algebra", SubjectID=subject.ID)
        subtask = factory.create_subtask(
            db_session, 
            TaskID=task.TaskID, 
            SubTaskNumber=1, 
            Description="What is 2+2?", 
            Answer="4"
        )
        
        # Act
        response = client.post("/api/v1/tasks/check-answer", json={
            "subtask_id": subtask.SubTaskID,
            "student_answer": "4"
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_correct"] is True
        assert data["data"]["score"] == 1.0
    
    def test_check_answer_incorrect(self, client: TestClient, db_session: Session, factory):
        """Test answer checking with incorrect answer."""
        # Arrange
        subject = factory.create_subject(db_session, Name="Mathematics")
        task = factory.create_task(db_session, TaskNumber=1, TaskTitle="Algebra", SubjectID=subject.ID)
        subtask = factory.create_subtask(
            db_session, 
            TaskID=task.TaskID, 
            SubTaskNumber=1, 
            Description="What is 2+2?", 
            Answer="4"
        )
        
        # Act
        response = client.post("/api/v1/tasks/check-answer", json={
            "subtask_id": subtask.SubTaskID,
            "student_answer": "5"
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_correct"] is False
        assert data["data"]["score"] == 0.0
    
    def test_check_answer_case_insensitive(self, client: TestClient, db_session: Session, factory):
        """Test that answer checking is case insensitive."""
        # Arrange
        subject = factory.create_subject(db_session, Name="Mathematics")
        task = factory.create_task(db_session, TaskNumber=1, TaskTitle="Algebra", SubjectID=subject.ID)
        subtask = factory.create_subtask(
            db_session, 
            TaskID=task.TaskID, 
            SubTaskNumber=1, 
            Description="What is the answer?", 
            Answer="YES"
        )
        
        # Act
        response = client.post("/api/v1/tasks/check-answer", json={
            "subtask_id": subtask.SubTaskID,
            "student_answer": "yes"
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_correct"] is True
        assert data["data"]["score"] == 1.0
    
    def test_check_answer_subtask_not_found(self, client: TestClient, db_session: Session):
        """Test answer checking for non-existent subtask."""
        # Act
        response = client.post("/api/v1/tasks/check-answer", json={
            "subtask_id": 999,
            "student_answer": "test"
        })
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_pagination(self, client: TestClient, db_session: Session, factory):
        """Test pagination functionality."""
        # Arrange
        subject = factory.create_subject(db_session, Name="Mathematics")
        for i in range(25):
            factory.create_task(db_session, TaskNumber=i+1, TaskTitle=f"Task {i+1}", SubjectID=subject.ID)
        
        # Act
        response = client.get("/api/v1/tasks?skip=10&limit=10")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 10
        # Should get tasks 11-20 (after skipping 10)
        assert data["data"][0]["task_number"] == 11
        assert data["data"][9]["task_number"] == 20
