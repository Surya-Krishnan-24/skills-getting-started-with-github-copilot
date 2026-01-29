"""
Tests for the activities API endpoints.
"""

import pytest


class TestGetActivities:
    """Test cases for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
    
    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Test that each activity has the correct structure."""
        response = client.get("/activities")
        data = response.json()
        
        # Check Chess Club structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_returns_initial_participants(self, client, reset_activities):
        """Test that participants are correctly returned."""
        response = client.get("/activities")
        data = response.json()
        
        # Check Chess Club has initial participants
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        
        # Check Basketball Team has no participants
        assert len(data["Basketball Team"]["participants"]) == 0


class TestSignUpForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Basketball Team/signup?email=student@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "student@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant."""
        # Sign up
        client.post("/activities/Basketball Team/signup?email=student@mergington.edu")
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert "student@mergington.edu" in activities["Basketball Team"]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for activity that doesn't exist."""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_at_max_capacity(self, client, reset_activities):
        """Test signup when activity is at max capacity."""
        # Get an activity with small capacity
        response = client.get("/activities")
        activities = response.json()
        
        # Math Club has max 10 participants
        # Try to sign up enough students to exceed capacity
        for i in range(10):
            email = f"student{i}@mergington.edu"
            client.post(f"/activities/Math Club/signup?email={email}")
        
        # Try to add one more - should fail
        response = client.post(
            "/activities/Math Club/signup?email=overflow@mergington.edu"
        )
        assert response.status_code == 400
        assert "maximum capacity" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Test cases for POST /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant."""
        # Unregister
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from activity that doesn't exist."""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test unregister when student is not registered."""
        response = client.post(
            "/activities/Basketball Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that a student can sign up again after unregistering."""
        # Unregister
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        # Sign up again
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant is back
        response = client.get("/activities")
        activities = response.json()
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]


class TestRoot:
    """Test cases for GET / endpoint."""
    
    def test_root_redirects(self, client, reset_activities):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
