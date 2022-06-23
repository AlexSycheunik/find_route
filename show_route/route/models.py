from django.db import models


class WayConfigurations(models.Model):
    class Meta:
        db_table = "way_config"
        verbose_name = "Характеристики дороги"
        verbose_name_plural = "Характеристики дорог"

    way_id = models.IntegerField(verbose_name="ID пути")
    truck_ban = models.BooleanField(verbose_name="Запрет на движение грузовых т.с.")
    weight_limit = models.FloatField(verbose_name="Ограничение по весу т.с.", default=0)
    way_height = models.FloatField(verbose_name="Высота коммуникаций и т.п.", default=0)
    way_width = models.FloatField(verbose_name="Ширина проезжей части", default=0)

    def __str__(self):
        return self.way_id


class SavedRoutes(models.Model):
    class Meta:
        db_table = "saved_routes"
        verbose_name = "Сохраненный путь"
        verbose_name_plural = "Сохраненные пути"

    start_point_lat = models.FloatField(verbose_name="Стартовая точка (широта)", default=0)
    start_point_long = models.FloatField(verbose_name="Стартовая точка (долгота)", default=0)
    end_point_lat = models.FloatField(verbose_name="Конечная точка (широта)", default=0)
    end_point_long = models.FloatField(verbose_name="Конечная точка (долгота)", default=0)
    route_file = models.FileField(verbose_name="Файл с маршрутом", upload_to='routes')

    def __str__(self):
        return self.start_point_lat
