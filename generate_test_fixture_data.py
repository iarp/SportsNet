# pragma: no cover
import datetime
import glob
import json
import os
import sys

import django
import environ
import psycopg2
import pyodbc

env = environ.Env()
environ.Env.read_env(".env")

DUMP_SK_DATA = False
RESET_DB_MIGRATIONS = True
DELETE_MIGRATION_FILES = False
USING_POSTGRES_INSTEAD_OF_SQLITE = True
VERBOSE = True


if DUMP_SK_DATA:
    connection = pyodbc.connect(
        f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={env.str('SK_HOSTNAME')};DATABASE={env.str('SK_DATABASE')};"
        f"UID={env.str('SK_USERNAME')};PWD={env.str('SK_PASSWORD')}",
        autocommit=False,
    )
    cursor = connection.cursor()

    tables = [
        "TeamStatus",
        "TeamStatusReason",
        "TeamStaffStatus",
        "TeamStaffStatusReason",
        "TeamStaffType",
        "TeamStaffTypeChangeAllowed",
        "TeamStaffTypeQual",
    ]

    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table} order by displayseq")
        except pyodbc.ProgrammingError:
            cursor.execute(f"SELECT * FROM {table}")

        output = {}
        weight = 0
        while True:
            item = cursor.fetchone()
            if not item:
                break
            weight += 1
            row = {}
            for i in cursor.description:
                column_name = i[0]
                column_type = i[1]

                column_data = getattr(item, column_name)
                if isinstance(column_data, (datetime.datetime, datetime.date)):
                    column_data = column_data.isoformat()

                row[column_name] = column_data

            row["weight"] = weight
            output[getattr(item, f"{table}Id")] = row

        with open(f"cache/HCC_Sports_Keeper/{table}.json", "w") as f:
            json.dump(output, f, indent=4)
    exit()


if RESET_DB_MIGRATIONS:

    if USING_POSTGRES_INSTEAD_OF_SQLITE:
        pg = psycopg2.connect(
            dbname=env.str("PG_DATABASE"),
            host=env.str("PG_HOSTNAME"),
            user=env.str("PG_USERNAME"),
            password=env.str("PG_PASSWORD"),
        )
        with pg.cursor() as cursor:
            cursor.execute(
                """DROP SCHEMA public CASCADE;
                    CREATE SCHEMA public;

                    GRANT ALL ON SCHEMA public TO postgres;
                    GRANT ALL ON SCHEMA public TO public;"""
            )
        pg.commit()
    else:
        try:
            os.unlink("db.sqlite3")
        except FileNotFoundError:
            pass

    if DELETE_MIGRATION_FILES:
        for app in ["core", "team"]:
            for file in glob.glob(f"{app}/migrations/0*.py"):
                os.unlink(file)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sportsnet.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from django.utils.text import slugify

call_command("makemigrations")
call_command("migrate")

from core.models import Division, League, Season, SubDivision
from team.models import (
    Staff,
    StaffStatus,
    StaffStatusReason,
    StaffType,
    Team,
    TeamStatus,
    TeamStatusReason,
)

User = get_user_model()

if RESET_DB_MIGRATIONS:
    with open("cache/HCC_Sports_Keeper/TeamStaffStatus.json", "r") as f:
        for _id, data in json.load(f).items():
            item, _ = StaffStatus.objects.get_or_create(
                old_sk_id=_id,
                name=data["Name"],
                weight=data["weight"],
                include_in_roster_export=data["IncludeInExportRoster"],
            )
            item.inserted = timezone.make_aware(
                datetime.datetime.fromisoformat(data["InsertDateTime"]),
                timezone.get_current_timezone(),
            )
            item.save(update_fields=["inserted"])

    with open("cache/HCC_Sports_Keeper/TeamStaffStatusReason.json", "r") as f:
        for _id, data in json.load(f).items():
            item, _ = StaffStatusReason.objects.get_or_create(
                old_sk_id=_id,
                name=data["Name"],
                weight=data["weight"],
            )
            item.inserted = timezone.make_aware(
                datetime.datetime.fromisoformat(data["InsertDateTime"]),
                timezone.get_current_timezone(),
            )
            item.save(update_fields=["inserted"])

    with open("cache/HCC_Sports_Keeper/TeamStaffType.json", "r") as f:
        for _id, data in json.load(f).items():
            item, _ = StaffType.objects.get_or_create(
                old_sk_id=_id,
                name=data["Name"],
                weight=data["weight"],
                required=data["Required"],
            )
            item.inserted = timezone.make_aware(
                datetime.datetime.fromisoformat(data["InsertDateTime"]),
                timezone.get_current_timezone(),
            )
            item.save(update_fields=["inserted"])

    with open("cache/HCC_Sports_Keeper/TeamStatus.json", "r") as f:
        for _id, data in json.load(f).items():
            item, _ = TeamStatus.objects.get_or_create(
                old_sk_id=_id,
                name=data["Name"],
                weight=data["weight"],
                include_in_roster_export=data["IncludeInExportRoster"],
                clear_changed_staff_players_flag=data["ClrChgdStfPlyrSts"],
            )
            item.inserted = timezone.make_aware(
                datetime.datetime.fromisoformat(data["InsertDateTime"]),
                timezone.get_current_timezone(),
            )
            item.save(update_fields=["inserted"])

    with open("cache/HCC_Sports_Keeper/TeamStatusReason.json", "r") as f:
        for _id, data in json.load(f).items():
            item, _ = TeamStatusReason.objects.get_or_create(
                old_sk_id=_id,
                name=data["Name"],
                weight=data["weight"],
                status=TeamStatus.objects.get(old_sk_id=data["TeamStatusId"]),
            )
            item.inserted = timezone.make_aware(
                datetime.datetime.fromisoformat(data["InsertDateTime"]),
                timezone.get_current_timezone(),
            )
            item.save(update_fields=["inserted"])


"""
2 Seasons
    2 Leagues
        2 Divisions
            2 SubDivisions
                2 Teams

48 teams total.
"""

if (
    Season.objects.count() > 2
    or League.objects.count() > 4
    or Division.objects.count() > 8
    or SubDivision.objects.count() > 16
    or Team.objects.count() > 32
    or User.objects.count() > 62
):
    print("#### WARNING ####")
    print("Object counts in core tables are greater than test fixture data generation.")
    if (
        input("Are you certain you want to clear all data and reset? (y/N):").lower()
        != "y"
    ):
        sys.exit()

Staff.objects.all().delete()
StaffType.objects.all().delete()
Team.objects.all().delete()
SubDivision.objects.all().delete()
Division.objects.all().delete()
League.objects.all().delete()
Season.objects.all().delete()
User.objects.all().delete()

type_coach, _ = StaffType.objects.get_or_create(name="Coach")
type_convenor, _ = StaffType.objects.get_or_create(name="Convenor")
type_vp, _ = StaffType.objects.get_or_create(name="VP")
type_admin, _ = StaffType.objects.get_or_create(name="Admin")

staff_status_approved, _ = StaffStatus.objects.get_or_create(name="APPROVED")
team_status_approved, _ = TeamStatus.objects.get_or_create(name="APPROVED")
team_status_reason, _ = TeamStatusReason.objects.get_or_create(old_sk_id=4)


def generate_email_address(data):
    return f"{slugify(data)}@domain.com"


def create_user(data):
    return User.objects.create(email=generate_email_address(data))


current_year = timezone.now().year
for s in range(current_year, current_year + 2):
    season = Season.objects.create(
        name=f"{s}-{s+1}",
        start=timezone.datetime(s, 9, 1),
        end=timezone.datetime(s + 1, 8, 31),
    )

    admin_user = create_user(f"{season} Admin")
    Staff.objects.create(
        season=season,
        type=type_admin,
        user=admin_user,
        status=staff_status_approved,
    )

    if VERBOSE:
        print(season)

    for league in ["HL", "REP"]:
        league = League.objects.create(name=league, season=season)

        if VERBOSE:
            print("\t", league)

        vp_user = create_user(f"{season} {league} VP")

        Staff.objects.create(
            type=type_vp,
            season=season,
            league=league,
            user=vp_user,
            status=staff_status_approved,
        )

        subdivision_listing = ["Blue", "White"]
        if league.name == "REP":
            subdivision_listing = ["A", "AA"]

        for division in ["U10", "U11"]:

            division = Division.objects.create(
                name=division, league=league, season=season
            )

            division_user = create_user(f"{season} {league} {division} Division")

            Staff.objects.create(
                type=type_vp,
                season=season,
                league=league,
                division=division,
                user=division_user,
                status=staff_status_approved,
            )

            if VERBOSE:
                print("\t\t", division, division_user)

            for subdivision in subdivision_listing:
                subdivision = SubDivision.objects.create(
                    name=subdivision,
                    division=division,
                    season=season,
                    league=league,
                )

                subdivision_user = create_user(
                    f"{season} - {league} - {division} - {subdivision} - SubDivision"
                )

                if VERBOSE:
                    print("\t\t\t", subdivision, subdivision_user, sep=" / ")

                Staff.objects.create(
                    type=type_convenor,
                    season=season,
                    league=league,
                    division=division,
                    subdivision=subdivision,
                    user=subdivision_user,
                    status=staff_status_approved,
                )

                for team in ["Graham", "Henry"]:
                    team = Team.objects.create(
                        season=season,
                        league=league,
                        division=division,
                        subdivision=subdivision,
                        name=team,
                        status=team_status_approved,
                        status_reason=team_status_reason,
                    )

                    coach_user = create_user(
                        f"{season} - {league} - {division} - {subdivision} - {team} - Coach"
                    )

                    Staff.objects.create(
                        type=type_coach,
                        season=season,
                        league=league,
                        division=division,
                        subdivision=subdivision,
                        team=team,
                        user=coach_user,
                        status=staff_status_approved,
                    )

                    if VERBOSE:
                        print("\t\t\t\t", team, coach_user, sep=" - ")

print("Seasons Generated:", Season.objects.count())
print("Leagues Generated:", League.objects.count())
print("Divisions Generated:", Division.objects.count())
print("SubDivisions Generated:", SubDivision.objects.count())
print("Teams Generated:", Team.objects.count())
print("Users Generated:", User.objects.count())

for app in ["core", "team"]:
    os.makedirs(f"{app}/fixtures/", exist_ok=True)
    with open(f"{app}/fixtures/test_fixtures.json", "w") as f:
        call_command("dumpdata", app, "--indent", "4", stdout=f)
