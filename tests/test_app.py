"""
Test suite for the FastAPI activities application.
Uses the AAA (Arrange-Act-Assert) testing pattern.
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_all_activities_success(self, client, reset_activities):
        """
        Arrange: Set up the test client
        Act: Send GET request to /activities
        Assert: Verify response status and structure
        """
        # Arrange
        expected_activity_names = [
            "Soccer Team",
            "Tennis Club",
            "Photography Club",
            "Music Band",
            "Robotics Club",
            "Math Olympiad Team"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 6

        for activity_name in expected_activity_names:
            assert activity_name in activities
            activity = activities[activity_name]
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)

    def test_get_activities_returns_empty_participants_initially(self, client, reset_activities):
        """
        Arrange: Set up the test client
        Act: Send GET request to /activities
        Assert: Verify all activities have empty participant lists initially
        """
        # Arrange & Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert activity_data["participants"] == []
            assert len(activity_data["participants"]) == 0


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_student_success(self, client, reset_activities):
        """
        Arrange: Prepare valid activity and student email
        Act: Send POST request to signup
        Assert: Verify student is added and response is correct
        """
        # Arrange
        activity_name = "Soccer Team"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"

        # Verify student was added to participants
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_multiple_students(self, client, reset_activities):
        """
        Arrange: Prepare multiple students for the same activity
        Act: Send multiple signup requests
        Assert: Verify all students are added
        """
        # Arrange
        activity_name = "Tennis Club"
        emails = [
            "alice@mergington.edu",
            "bob@mergington.edu",
            "charlie@mergington.edu"
        ]

        # Act
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert
        activities_response = client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]

        for email in emails:
            assert email in participants
        assert len(participants) == 3

    def test_signup_activity_not_found(self, client, reset_activities):
        """
        Arrange: Prepare request for non-existent activity
        Act: Send POST request to signup
        Assert: Verify 404 error is returned
        """
        # Arrange
        invalid_activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_duplicate_student(self, client, reset_activities):
        """
        Arrange: Sign up a student, then attempt to sign them up again
        Act: Send first signup request, then second signup request
        Assert: Second request returns 400 error
        """
        # Arrange
        activity_name = "Photography Club"
        email = "student@mergington.edu"

        # Act - First signup
        first_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert first_response.status_code == 200

        # Act - Duplicate signup
        second_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert second_response.status_code == 400
        data = second_response.json()
        assert data["detail"] == "Student is already signed up"

    def test_signup_preserves_other_activity_participants(self, client, reset_activities):
        """
        Arrange: Set up participants in multiple activities
        Act: Sign up a new student for one activity
        Assert: Verify other activities' participants are unchanged
        """
        # Arrange
        soccer_students = ["alice@mergington.edu", "bob@mergington.edu"]
        tennis_students = ["charlie@mergington.edu"]

        # Sign up students to different activities
        for email in soccer_students:
            client.post("/activities/Soccer Team/signup", params={"email": email})

        for email in tennis_students:
            client.post("/activities/Tennis Club/signup", params={"email": email})

        # Act
        new_student = "david@mergington.edu"
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": new_student}
        )

        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()

        assert new_student in activities["Soccer Team"]["participants"]
        assert len(activities["Soccer Team"]["participants"]) == 3
        assert activities["Tennis Club"]["participants"] == tennis_students


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_student_success(self, client, reset_activities):
        """
        Arrange: Sign up a student, then prepare to unregister them
        Act: Send DELETE request to unregister
        Assert: Verify student is removed and response is correct
        """
        # Arrange
        activity_name = "Music Band"
        email = "student@mergington.edu"

        # Sign up the student first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"

        # Verify student was removed from participants
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client, reset_activities):
        """
        Arrange: Prepare request for non-existent activity
        Act: Send DELETE request to unregister
        Assert: Verify 404 error is returned
        """
        # Arrange
        invalid_activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_student_not_registered(self, client, reset_activities):
        """
        Arrange: Attempt to unregister a student who is not signed up
        Act: Send DELETE request to unregister
        Assert: Verify 400 error is returned
        """
        # Arrange
        activity_name = "Robotics Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"

    def test_unregister_one_of_multiple_students(self, client, reset_activities):
        """
        Arrange: Sign up multiple students, then unregister one
        Act: Send DELETE request for one student
        Assert: Verify only that student is removed, others remain
        """
        # Arrange
        activity_name = "Math Olympiad Team"
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]

        for email in emails:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )

        email_to_remove = "bob@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )

        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]

        assert email_to_remove not in participants
        assert "alice@mergington.edu" in participants
        assert "charlie@mergington.edu" in participants
        assert len(participants) == 2

    def test_signup_and_unregister_sequence(self, client, reset_activities):
        """
        Arrange: Set up a sequence of signup and unregister operations
        Act: Perform the sequence
        Assert: Verify final state is consistent
        """
        # Arrange
        activity_name = "Photography Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act - Signup both students
        client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{activity_name}/signup", params={"email": email2})

        # Verify both are signed up
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert len(activities[activity_name]["participants"]) == 2

        # Unregister first student
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email1}
        )
        assert response1.status_code == 200

        # Verify only second student remains
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert activities[activity_name]["participants"] == [email2]

        # Sign up first student again
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        assert response2.status_code == 200

        # Verify both are signed up again
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert len(activities[activity_name]["participants"]) == 2
        assert email1 in activities[activity_name]["participants"]
