from django.db import models


class Technology(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Developer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    technologies = models.ManyToManyField(Technology, related_name='developers')

    def __str__(self):
        return self.name


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    technologies = models.ManyToManyField(Technology, related_name='projects')
    planned_hours = models.PositiveIntegerField(editable=False)

    HOURS_PER_DAY = 8

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"

    def save(self, *args, **kwargs):
        # Planned hours = calendar days in the period (inclusive) * 8h work day.
        if self.start_date and self.end_date:
            days = (self.end_date - self.start_date).days + 1
            self.planned_hours = days * self.HOURS_PER_DAY
        super().save(*args, **kwargs)


class Allocation(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='allocations')
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name='allocations')
    hours = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.developer.name} allocated to {self.project.name} for {self.hours} hours"
