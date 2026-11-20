from django.db import migrations


def create_ia_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    administrador, _ = Group.objects.get_or_create(name="Administrador de IA")
    usuario, _ = Group.objects.get_or_create(name="Usuário de IA")

    ia_permissions = Permission.objects.filter(
        content_type__app_label="ia",
    )
    administrador.permissions.set(ia_permissions)
    usuario.permissions.set(
        ia_permissions.filter(
            codename__in=[
                "view_conversa",
                "usar_ia",
                "view_mensagem",
                "view_consumoia",
                "view_requisicaoia",
            ]
        )
    )


def remove_ia_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["Administrador de IA", "Usuário de IA"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("ia", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_ia_groups, remove_ia_groups),
    ]
