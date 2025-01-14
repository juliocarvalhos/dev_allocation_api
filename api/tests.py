from datetime import date, timedelta
from django.test import TestCase
from api.models import Project, Developer, Technology
from api.serializers import AllocationSerializer

class AllocationSerializerTestCase(TestCase):
    def setUp(self):
        # Criação das tecnologias
        self.python_technology = Technology.objects.create(name="Python")
    
        # Criação do projeto com datas próximas da data atual (para o teste válido)
        self.project = Project.objects.create(
            name="Test Project",
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() + timedelta(days=5),
        )

        # Associação da tecnologia ao projeto
        self.project.technologies.add(self.python_technology)

        # Criação do desenvolvedor
        self.developer = Developer.objects.create(name="John Doe")

        # Associação da tecnologia ao desenvolvedor
        self.developer.technologies.add(self.python_technology)

        # Criação de um projeto no futuro (para o teste de datas fora do intervalo)
        self.future_project = Project.objects.create(
            name="Future Test Project",
            start_date=date.today() + timedelta(days=10),  # Data no futuro
            end_date=date.today() + timedelta(days=20),   # Data no futuro
        )
        self.future_project.technologies.add(self.python_technology)

    def test_valid_allocation(self):
        # Testa a criação de uma alocação válida
        data = {
            "project": self.project.id,
            "developer": self.developer.id,
            "hours": 20,
        }
        serializer = AllocationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_allocation_exceeds_planned_hours(self):
        allocation_data = {
            "project": self.project.id,
            "developer": self.developer.id,
            "hours": 120,  # Exceeds planned hours
        }
        serializer = AllocationSerializer(data=allocation_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors['non_field_errors'][0],
            f"Allocating 120 hours exceeds the planned hours for the project '{self.project.name}'. "
            f"Currently allocated: 0 hours, planned: {self.project.planned_hours} hours."
        )

    def test_allocation_outside_project_dates(self):
        # Teste com o projeto futuro
        allocation_data = {
            "project": self.future_project.id,
            "developer": self.developer.id,
            "hours": 20,
        }

        # A data do projeto está no futuro, então a data de alocação deve estar fora do intervalo
        serializer = AllocationSerializer(data=allocation_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors['non_field_errors'][0],
            f"The current date ({date.today()}) is outside the project's start and end dates "
            f"({self.future_project.start_date} to {self.future_project.end_date})."
        )

    def test_developer_missing_required_technologies(self):
        # Remove a tecnologia do desenvolvedor
        self.developer.technologies.clear()

        # Testa a criação de uma alocação
        data = {
            "project": self.project.id,
            "developer": self.developer.id,
            "hours": 20,
        }
        serializer = AllocationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            f"The developer '{self.developer.name}' does not have the required technologies for the project '{self.project.name}'.",
        )
