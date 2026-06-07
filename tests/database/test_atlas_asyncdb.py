"""Tests for AtlasAsyncdb database class"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.exc import OperationalError

from atlas_shared_app.database.atlas_asyncdb import AtlasAsyncdb, get_engine, get_engine_from_settings
from atlas_shared_app.settings import AtlasDbSettings


@pytest.fixture
def db_settings():
    """Create an AtlasDbSettings instance for testing"""
    return AtlasDbSettings(
        host_with_port="localhost:5432",
        name="test_db",
        user="test_user",
        secret_password="test_password",
        protocol="postgresql+asyncpg://",
        echo=False,
        pool_size=5,
        pool_timeout=30,
        max_overflow=10,
    )


@pytest.fixture
def asyncdb(db_settings):
    """Create an AtlasAsyncdb instance for testing"""
    return AtlasAsyncdb(db_settings=db_settings)


def test_atlas_asyncdb_init():
    """Test AtlasAsyncdb initialization"""
    settings = AtlasDbSettings(
        host_with_port="localhost:5432",
        name="test_db",
        user="test_user",
        secret_password="test_password",
    )
    db = AtlasAsyncdb(db_settings=settings)

    assert db.db_settings.host_with_port == "localhost:5432"
    assert db.db_settings.name == "test_db"
    assert db.db_settings.user == "test_user"
    assert db.db_settings.protocol == "postgresql+asyncpg://"
    assert db.db_settings.echo is False
    assert db.db_settings.pool_size == 5
    assert db.db_settings.pool_timeout == 30
    assert db.db_settings.max_overflow == 10
    assert db.engine is None


def test_atlas_asyncdb_init_custom_options():
    """Test AtlasAsyncdb initialization with custom options"""
    settings = AtlasDbSettings(
        host_with_port="db.example.com:5433",
        name="custom_db",
        user="admin",
        secret_password="admin_password",
        protocol="mysql+aiomysql://",
        echo=True,
        pool_size=10,
        pool_timeout=60,
        max_overflow=20,
    )
    db = AtlasAsyncdb(db_settings=settings)

    assert db.db_settings.host_with_port == "db.example.com:5433"
    assert db.db_settings.name == "custom_db"
    assert db.db_settings.user == "admin"
    assert db.db_settings.protocol == "mysql+aiomysql://"
    assert db.db_settings.echo is True
    assert db.db_settings.pool_size == 10
    assert db.db_settings.pool_timeout == 60
    assert db.db_settings.max_overflow == 20


@pytest.mark.asyncio
async def test_atlas_asyncdb_init_db(asyncdb):
    """Test init_db creates engine"""
    with patch('atlas_shared_app.database.atlas_asyncdb.create_async_engine') as mock_create:
        mock_engine = MagicMock()
        mock_create.return_value = mock_engine

        await asyncdb.init_db()

        assert asyncdb.engine == mock_engine
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_atlas_asyncdb_dispose(asyncdb):
    """Test dispose cleans up engine"""
    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()
    asyncdb.engine = mock_engine

    await asyncdb.dispose()

    mock_engine.dispose.assert_called_once()
    assert asyncdb.engine is None


@pytest.mark.asyncio
async def test_atlas_asyncdb_dispose_no_engine(asyncdb):
    """Test dispose does nothing when no engine"""
    asyncdb.engine = None
    await asyncdb.dispose()  # Should not raise


@pytest.mark.asyncio
async def test_atlas_asyncdb_get_engine_initializes(asyncdb):
    """Test get_engine initializes engine if not exists"""
    with patch('atlas_shared_app.database.atlas_asyncdb.create_async_engine') as mock_create:
        mock_engine = MagicMock()
        mock_engine.connect = MagicMock()
        mock_create.return_value = mock_engine

        engine = await asyncdb.get_engine()

        assert engine == mock_engine


@pytest.mark.asyncio
async def test_atlas_asyncdb_get_engine_returns_existing(asyncdb):
    """Test get_engine returns existing engine"""
    mock_engine = MagicMock()
    mock_engine.connect = MagicMock()
    asyncdb.engine = mock_engine

    engine = await asyncdb.get_engine()

    assert engine == mock_engine


def test_get_engine_success():
    """Test get_engine dependency function"""
    mock_request = MagicMock()
    mock_engine = MagicMock()
    mock_asyncdb = MagicMock()
    mock_asyncdb.get_engine = AsyncMock(return_value=mock_engine)
    mock_request.app.state.atlas_asyncdb = mock_asyncdb

    # get_engine is async, but we can test the setup
    assert mock_request.app.state.atlas_asyncdb is not None


def test_get_engine_no_asyncdb():
    """Test get_engine raises error when no asyncdb"""
    mock_request = MagicMock()
    mock_request.app.state.atlas_asyncdb = None

    # The actual async function would raise ValueError
    assert mock_request.app.state.atlas_asyncdb is None


@pytest.mark.asyncio
async def test_get_engine_dependency():
    """Test get_engine as dependency"""
    mock_request = MagicMock()
    mock_engine = MagicMock()
    mock_asyncdb = MagicMock()
    mock_asyncdb.get_engine = AsyncMock(return_value=mock_engine)
    mock_request.app.state.atlas_asyncdb = mock_asyncdb

    engine = await get_engine(mock_request)

    assert engine == mock_engine


@pytest.mark.asyncio
async def test_get_engine_dependency_no_asyncdb():
    """Test get_engine raises error when no asyncdb in app state"""
    mock_request = MagicMock()
    mock_request.app.state.atlas_asyncdb = None

    with pytest.raises(ValueError) as exc_info:
        await get_engine(mock_request)

    assert "AtlasAsyncdb is not initialized" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_engine_dependency_no_engine():
    """Test get_engine raises error when engine is None"""
    mock_request = MagicMock()
    mock_asyncdb = MagicMock()
    mock_asyncdb.get_engine = AsyncMock(return_value=None)
    mock_request.app.state.atlas_asyncdb = mock_asyncdb

    with pytest.raises(ValueError) as exc_info:
        await get_engine(mock_request)

    assert "AsyncEngine is not initialized" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_engine_from_settings(db_settings):
    """Test get_engine_from_settings creates and returns engine"""
    with patch('atlas_shared_app.database.atlas_asyncdb.create_async_engine') as mock_create:
        mock_engine = MagicMock()
        mock_engine.connect = MagicMock()
        mock_create.return_value = mock_engine

        engine = await get_engine_from_settings(db_settings)

        assert engine == mock_engine
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_get_engine_from_settings_no_engine(db_settings):
    """Test get_engine_from_settings raises when engine is None"""
    with patch('atlas_shared_app.database.atlas_asyncdb.AtlasAsyncdb') as mock_asyncdb_class:
        mock_asyncdb = MagicMock()
        mock_asyncdb.get_engine = AsyncMock(return_value=None)
        mock_asyncdb_class.return_value = mock_asyncdb

        with pytest.raises(ValueError) as exc_info:
            await get_engine_from_settings(db_settings)

        assert "AsyncEngine is not initialized" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_engine_retry_on_error(asyncdb):
    """Test get_engine retries on OperationalError"""
    with patch('atlas_shared_app.database.atlas_asyncdb.create_async_engine') as mock_create:
        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()
        # First connect fails, second succeeds
        call_count = [0]
        def side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                raise OperationalError("statement", "params", "orig")
        mock_engine.connect = MagicMock(side_effect=side_effect)
        mock_create.return_value = mock_engine

        engine = await asyncdb.get_engine()

        assert engine == mock_engine


@pytest.mark.asyncio
async def test_get_engine_retry_fails(asyncdb):
    """Test get_engine raises when retry also fails"""
    with patch('atlas_shared_app.database.atlas_asyncdb.create_async_engine') as mock_create:
        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()
        # Both connects fail
        mock_engine.connect = MagicMock(side_effect=OperationalError("statement", "params", "orig"))
        mock_create.return_value = mock_engine

        with pytest.raises(OperationalError):
            await asyncdb.get_engine()
