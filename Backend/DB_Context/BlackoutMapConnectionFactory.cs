using System.Data;
using System.Data.SQLite;
using Dapper;

public interface IBlackoutMapConnectionFactory
{
    Task<SQLiteConnection> CreateConnectionAsync();
}

public class BlackoutMapConnectionFactory : IBlackoutMapConnectionFactory
{
    private string _connectionString = string.Empty;

    public BlackoutMapConnectionFactory(string connectionsString)
    {
        this._connectionString = connectionsString;    
    }

    public async Task<SQLiteConnection> CreateConnectionAsync()
    {
        SQLiteConnection dbConnection = new SQLiteConnection(this._connectionString);
        await dbConnection.OpenAsync();
        return dbConnection;
    }
}

