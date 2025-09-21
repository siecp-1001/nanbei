from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import datetime
from django.core.validators import MinValueValidator

# Custom Managers
class Activemanager(models.Manager):
    def active(self):
        return self.filter(active=True)


class producttagmanager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


# Product Tags
class producttag(models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    objects = producttagmanager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


# Product Model
class product(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(max_length=48)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)
    objects = Activemanager()
    tags = models.ManyToManyField(producttag, blank=True)

    def __str__(self):
        return self.name


# Product Images
class productimage(models.Model):
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product-images")
    thumbnail = models.ImageField(upload_to="product-thumbnails", null=True)


# User Manager
class usermanager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


# Custom User
class user(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = usermanager()


# Address Model
class adress(models.Model):
    supported_countries = (
        ("uk", "United Kingdom"),
        ("us", "United States of America"),
        ("eg", "Egypt"),
    )
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    fromv = models.CharField("From", max_length=60)
    to = models.CharField("To", max_length=60, blank=True)
    driver = models.CharField("Driver", max_length=12)
    city = models.CharField(max_length=60)
    country = models.CharField(max_length=3, choices=supported_countries)

    def __str__(self):
        return ",".join([self.name, self.fromv, self.to, self.driver, self.city, self.country])


# Chat Room & Message
class Room(models.Model):
    name = models.CharField(max_length=255)


class Message(models.Model):
    value = models.TextField()
    date = models.DateTimeField(default=datetime.now, blank=True)
    user = models.CharField(max_length=255)
    room = models.CharField(max_length=255)


# Basket Models
class basket(models.Model):
    OPEN = 10
    SUBMITTED = 20
    STATUSES = (
        (OPEN, "Open"),
        (SUBMITTED, "Submitted"),
    )
    user = models.ForeignKey(user, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=OPEN)

    def is_empty(self):
        return self.basketline_set.all().count() == 0

    def count(self):
        return sum(i.quantity for i in self.basketline_set.all())


class basketline(models.Model):
    basket = models.ForeignKey(basket, on_delete=models.CASCADE)
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])


# Notes Model
class notes(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    NOTE = models.TextField()
    date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f"{self.NOTE[:50]} - {self.date}"


# Contact Model
class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


# OptionBase Abstract Model
class OptionBase(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


# Specific Option Models
class ProgramOption(OptionBase):
    pass


class DriverOption(OptionBase):
    pass


class CarOption(OptionBase):
    pass


class GuideOption(OptionBase):
    pass


class HotelOption(OptionBase):
    pass


class FlightOption(OptionBase):
    pass


# Tour Program Model
class TourProgram(models.Model):
    date = models.DateField(verbose_name="Tour Date")
    program_options = models.ManyToManyField(ProgramOption, blank=True, verbose_name="Programs")
    driver_options = models.ManyToManyField(DriverOption, blank=True, verbose_name="Drivers")
    car_options = models.ManyToManyField(CarOption, blank=True, verbose_name="Cars")
    guide_options = models.ManyToManyField(GuideOption, blank=True, verbose_name="Tour Guides")
    hotel_options = models.ManyToManyField(HotelOption, blank=True, verbose_name="Hotels")
    flight_options = models.ManyToManyField(FlightOption, blank=True, verbose_name="Flights")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Tour Program #{self.id}"
