import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Garantir que o diretório do app está no path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.database import Base, get_db
from app.models import Match, MatchStats

# Banco de dados em memória para testes
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Cria as tabelas no banco de dados de teste uma vez por sessão."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_database():
    """Limpa todas as tabelas antes de cada teste."""
    # Limpar tabelas na ordem correta (filhas primeiro)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM match_stats"))
        conn.execute(text("DELETE FROM matches"))
        conn.execute(text("DELETE FROM players"))
        conn.execute(text("DELETE FROM teams"))
    yield


def override_get_db():
    """Sobrescreve a dependência get_db para usar o banco de teste."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Fornece um cliente de teste FastAPI."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Fornece uma sessão de banco de dados de teste."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_team_data():
    """Dados de exemplo para criar um time."""
    return {
        "name": "Flamengo",
        "short_name": "FLA",
        "country": "Brasil",
        "league": "Serie-A",
        "stadium": "Maracanã",
        "founded": 1895,
        "fbref_id": "flamengo",
    }


@pytest.fixture
def sample_team2_data():
    """Dados de exemplo para um segundo time."""
    return {
        "name": "Palmeiras",
        "short_name": "PAL",
        "country": "Brasil",
        "league": "Serie-A",
        "stadium": "Allianz Parque",
        "founded": 1914,
        "fbref_id": "palmeiras",
    }


@pytest.fixture
def sample_player_data(sample_team_data, client):
    """Dados de exemplo para criar um jogador."""
    # Criar um time primeiro
    team = client.post("/api/v1/teams/", json=sample_team_data).json()
    return {
        "name": "Gabriel Barbosa",
        "full_name": "Gabriel Barbosa Almeida",
        "nationality": "Brasil",
        "position": "FW",
        "shirt_number": 9,
        "team_id": team["id"],
        "fbref_id": "gabriel-barbosa",
    }


@pytest.fixture
def sample_match_data(sample_team_data, sample_team2_data, client):
    """Dados de exemplo para criar uma partida."""
    team1 = client.post("/api/v1/teams/", json=sample_team_data).json()
    team2 = client.post("/api/v1/teams/", json=sample_team2_data).json()
    return {
        "home_team_id": team1["id"],
        "away_team_id": team2["id"],
        "competition": "Serie-A",
        "season": "2024-2025",
        "home_score": 2,
        "away_score": 1,
        "fbref_id": "match-123",
    }, team1, team2


@pytest.fixture
def sample_stats_data(sample_match_data, db_session, client):
    """Cria times, partida e estatísticas para testar previsões."""
    match_data, team1, team2 = sample_match_data
    match = client.post("/api/v1/matches/", json=match_data).json()

    # Criar estatísticas diretamente no banco
    home_stats = MatchStats(
        match_id=match["id"],
        team_id=team1["id"],
        is_home=True,
        possession=55.0,
        shots=15,
        shots_on_target=6,
        xg=2.1,
        xg_against=0.8,
        passes=450,
        pass_accuracy=85.0,
    )
    db_session.add(home_stats)

    away_stats = MatchStats(
        match_id=match["id"],
        team_id=team2["id"],
        is_home=False,
        possession=45.0,
        shots=10,
        shots_on_target=3,
        xg=0.9,
        xg_against=2.0,
        passes=380,
        pass_accuracy=80.0,
    )
    db_session.add(away_stats)
    db_session.commit()

    return team1, team2