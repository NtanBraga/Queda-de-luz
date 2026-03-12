using System.Data.SQLite;
using Dapper;
using Microsoft.AspNetCore.Mvc.ApplicationParts;

public class CidadeService : ICidadeService
{
    private IBlackoutMapConnectionFactory _dbConnectionFactory;
    public CidadeService(IBlackoutMapConnectionFactory connectionFactory)
    {
        this._dbConnectionFactory = connectionFactory;
    }

    public async Task<Cidade> CreateCidadeAsync(Cidade cidade)
    {
        using SQLiteConnection dbContext = await this._dbConnectionFactory.CreateConnectionAsync();

        await dbContext.ExecuteAsync(
            """
                 INSERT INTO  Cidade (Nome_cidade, Estado_sigla)
                 VALUES (@nome, @estadoSigla)
            """,
            new { nome = cidade.Nome, estadoSigla = cidade.EstadoSigla}
        );

        await dbContext.CloseAsync();
        
        return cidade;
    }

}

public interface ICidadeService
{
    public Task<Cidade> CreateCidadeAsync(Cidade cidade);
}