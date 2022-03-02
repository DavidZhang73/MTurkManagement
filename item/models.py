from djongo import models


class SubCategory(models.Model):
    name = models.CharField(max_length=256, primary_key=True)
    url = models.URLField()

    class Meta:
        managed = False


class Category(models.Model):
    _id = models.ObjectIdField()
    name = models.CharField(max_length=256)
    subCategoryList = models.ArrayField(SubCategory)

    class Meta:
        managed = False
        db_table = "category"

    class Param:
        db = 'mongo'

    def __str__(self):
        return self.name


class Annotation(models.Model):
    manual = models.IntegerField(primary_key=True)
    page = models.IntegerField()
    step = models.IntegerField()
    color = models.CharField(max_length=8)
    highlight = models.BooleanField()
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    class Meta:
        managed = False


class Page(models.Model):
    pathname = models.CharField(max_length=156, primary_key=True)


class Manual(models.Model):
    url = models.URLField(primary_key=True)
    pathname = models.CharField(max_length=512)
    pageList = models.ArrayField(Page)

    class Meta:
        managed = False


class VideoAnnotation(models.Model):
    start = models.FloatField(primary_key=True)
    end = models.FloatField()
    manual = models.IntegerField()
    page = models.IntegerField()
    step = models.IntegerField()
    description = models.TextField()

    class Meta:
        managed = False


class Video(models.Model):
    url = models.URLField(primary_key=True)
    annotationList = models.ArrayField(VideoAnnotation)

    class Meta:
        managed = False


class Item(models.Model):
    _id = models.ObjectIdField()
    id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    typeName = models.CharField(max_length=256)
    category = models.CharField(max_length=256)
    subCategory = models.CharField(max_length=256)
    pipUrl = models.URLField()
    mainImageUrl = models.URLField()
    mainImagePathname = models.CharField(max_length=512)

    progressStatus = models.JSONField()
    variants = models.JSONField()

    annotationList = models.ArrayField(Annotation)
    manualList = models.ArrayField(Manual)
    videoList = models.ArrayField(Video)

    class Meta:
        managed = False
        db_table = "item"

    class Param:
        db = 'mongo'

    def __str__(self):
        return self.name
