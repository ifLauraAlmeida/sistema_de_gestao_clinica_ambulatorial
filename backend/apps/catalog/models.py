import uuid

from django.db import models

from apps.professionals.models import Specialty


class ServiceType(models.TextChoices):
    """Natureza do serviço; evita tratar exames e sessões como consulta médica."""

    CONSULTA = "CONSULTA", "Consulta"
    SESSAO = "SESSAO", "Sessão"
    PROCEDIMENTO = "PROCEDIMENTO", "Procedimento"
    EXAME = "EXAME", "Exame"


class Laterality(models.TextChoices):
    """Lado do corpo; atributo do agendamento em vez de serviços duplicados."""

    DIREITA = "DIREITA", "Direita"
    ESQUERDA = "ESQUERDA", "Esquerda"
    BILATERAL = "BILATERAL", "Bilateral"


class ServiceCategory(models.Model):
    """Área do catálogo, por exemplo "Raios-X" ou "Consultas e atendimentos"."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("nome", max_length=100, unique=True)
    display_order = models.PositiveSmallIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativa", default=True)

    class Meta:
        verbose_name = "área do catálogo"
        verbose_name_plural = "áreas do catálogo"
        ordering = ("display_order", "name")

    def __str__(self) -> str:
        return self.name


class ServiceGroup(models.Model):
    """Grupo dentro da área, por exemplo "Coluna" em Raios-X ou "Nutrição" em Consultas."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name="groups")
    name = models.CharField("nome", max_length=100)
    display_order = models.PositiveSmallIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "grupo de serviços"
        verbose_name_plural = "grupos de serviços"
        ordering = ("display_order", "name")
        constraints = [
            models.UniqueConstraint(fields=("category", "name"), name="service_group_unique_name"),
        ]

    def __str__(self) -> str:
        return f"{self.category} → {self.name}"


class FormFieldType(models.TextChoices):
    TEXT = "TEXT", "Texto curto"
    TEXTAREA = "TEXTAREA", "Texto longo"
    NUMBER = "NUMBER", "Número"
    BOOLEAN = "BOOLEAN", "Sim/Não"
    SELECT = "SELECT", "Lista de opções"
    TIME = "TIME", "Horário"


class ExecutionFormTemplate(models.Model):
    """
    Modelo de campos preenchidos na execução de um procedimento.

    Reutilizado por vários serviços (ex.: todos os raios-X usam "Radiografia"),
    para que o catálogo não precise repetir a definição de campos.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("nome", max_length=100, unique=True)
    description = models.CharField("descrição", max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "formulário de execução"
        verbose_name_plural = "formulários de execução"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class ExecutionFormField(models.Model):
    """Campo de um formulário de execução."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ExecutionFormTemplate, on_delete=models.CASCADE, related_name="fields"
    )
    key = models.SlugField("chave", max_length=50)
    label = models.CharField("rótulo", max_length=100)
    field_type = models.CharField("tipo", max_length=16, choices=FormFieldType.choices)
    unit = models.CharField("unidade", max_length=20, blank=True, default="")
    options = models.JSONField("opções", default=list, blank=True)
    is_required = models.BooleanField("obrigatório", default=False)
    display_order = models.PositiveSmallIntegerField("ordem", default=0)

    class Meta:
        verbose_name = "campo do formulário"
        verbose_name_plural = "campos do formulário"
        ordering = ("display_order", "label")
        constraints = [
            models.UniqueConstraint(fields=("template", "key"), name="form_field_unique_key"),
            models.CheckConstraint(
                condition=models.Q(field_type__in=FormFieldType.values),
                name="form_field_type_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.template}: {self.label}"


class Service(models.Model):
    """
    Serviço agendável: consulta, sessão, procedimento ou exame.

    A especialidade define quem executa (profissionais vinculados) e o prefixo
    da senha. Lateralidade e sedação são atributos do agendamento, não serviços
    separados.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(ServiceGroup, on_delete=models.PROTECT, related_name="services")
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, related_name="services")
    name = models.CharField("nome", max_length=150)
    service_type = models.CharField("tipo", max_length=16, choices=ServiceType.choices)
    duration_minutes = models.PositiveSmallIntegerField("duração (min)", default=30)
    # Valor de referência para gestão; cobrança e convênios ficam no módulo financeiro.
    reference_price = models.DecimalField(
        "preço de referência", max_digits=10, decimal_places=2, null=True, blank=True
    )
    requires_laterality = models.BooleanField("exige lateralidade", default=False)
    allows_sedation = models.BooleanField("permite sedação", default=False)
    is_laboratory_collection = models.BooleanField("coleta laboratorial", default=False)
    preparation_instructions = models.TextField("preparo", blank=True, default="")
    form_template = models.ForeignKey(
        ExecutionFormTemplate,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="services",
        verbose_name="formulário de execução",
    )
    display_order = models.PositiveSmallIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "serviço"
        verbose_name_plural = "serviços"
        ordering = ("display_order", "name")
        constraints = [
            models.UniqueConstraint(fields=("group", "name"), name="service_unique_name_in_group"),
            models.CheckConstraint(
                condition=models.Q(service_type__in=ServiceType.values),
                name="service_type_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(duration_minutes__gt=0), name="service_duration_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(reference_price__isnull=True) | models.Q(reference_price__gte=0),
                name="service_price_not_negative",
            ),
        ]
        indexes = [models.Index(fields=("name",), name="service_name_idx")]

    def __str__(self) -> str:
        return self.name


class ServiceAlias(models.Model):
    """Sinônimo usado na busca, por exemplo "Ergometria" para "Teste ergométrico"."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="aliases")
    name = models.CharField("sinônimo", max_length=150)

    class Meta:
        verbose_name = "sinônimo"
        verbose_name_plural = "sinônimos"
        constraints = [
            models.UniqueConstraint(fields=("service", "name"), name="service_alias_unique"),
        ]

    def __str__(self) -> str:
        return self.name


class SampleType(models.TextChoices):
    SANGUE = "SANGUE", "Sangue"
    URINA = "URINA", "Urina"
    FEZES = "FEZES", "Fezes"
    OUTRO = "OUTRO", "Outro"


class LaboratoryExam(models.Model):
    """
    Exame laboratorial. Tabela própria para não inflar o catálogo de serviços:
    é solicitado dentro do serviço de coleta laboratorial.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("nome", max_length=150, unique=True)
    group = models.CharField("grupo", max_length=100)
    sample_type = models.CharField("amostra", max_length=16, choices=SampleType.choices)
    preparation = models.TextField("preparo", blank=True, default="")
    fasting_hours = models.PositiveSmallIntegerField("jejum (horas)", default=0)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "exame laboratorial"
        verbose_name_plural = "exames laboratoriais"
        ordering = ("group", "name")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(sample_type__in=SampleType.values),
                name="laboratory_exam_sample_type_valid",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class ServicePackage(models.Model):
    """Pacote comercial (ex.: check-up preventivo) composto de serviços e exames."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("nome", max_length=150, unique=True)
    description = models.TextField("descrição", blank=True, default="")
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "pacote"
        verbose_name_plural = "pacotes"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class ServicePackageItem(models.Model):
    """Item do pacote: um serviço OU um exame laboratorial."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(
        Service, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    laboratory_exam = models.ForeignKey(
        LaboratoryExam, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    display_order = models.PositiveSmallIntegerField("ordem", default=0)

    class Meta:
        verbose_name = "item do pacote"
        verbose_name_plural = "itens do pacote"
        ordering = ("display_order",)
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(service__isnull=False, laboratory_exam__isnull=True)
                    | models.Q(service__isnull=True, laboratory_exam__isnull=False)
                ),
                name="package_item_service_xor_exam",
            ),
        ]

    def __str__(self) -> str:
        return str(self.service or self.laboratory_exam)
