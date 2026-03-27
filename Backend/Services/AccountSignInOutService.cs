using System.Text.Json;
using Dapper;

public class AccountSignInOutService : IAccountSignInOutService
{
    private IBlackoutMapConnectionFactory _connectionFactory;

    public AccountSignInOutService(IBlackoutMapConnectionFactory connectionFactory)
    {
        this._connectionFactory = connectionFactory;
    }

    public string HashPassword(string unhashedPassword)
    {
        //<<TODO:to integrate hashing algorithms>>
        return unhashedPassword;
    }


    public async Task<BaseAccount> CreateAccountAsync(BaseAccount baseAccount)
    { 
        using var dbcontext = await this._connectionFactory.CreateConnectionAsync();

        long accountId = await dbcontext.QuerySingleAsync<long>(
            """
                INSERT INTO Base_Account (Username, Hashed_password, Email, District_id)
                VALUES (@Username, @Hashed_password, @Email, @District_id)
                RETURNING Base_Account_id;
            """,
            new{ Username = baseAccount.Username, Hashed_password = baseAccount.HashedPassword, 
                 Email = baseAccount.Email, District_id = baseAccount.DistrictId}
        );

        switch(baseAccount)
        {
            case PersonAccount pAccount: 
                pAccount = await dbcontext.QuerySingleAsync<PersonAccount>(
                """
                    INSERT INTO Person_Account (Person_Account_id, Birthday)
                    VALUES (@AccountId, @Birthday);

                    SELECT pa.Birthday, 
                           ba.Username, ba.Email, ba.UTC_datetime_creation, 
                           ba.Advertisement_slots_amount, ba.District_id
                    FROM Person_Account AS pa JOIN Base_Account AS ba ON pa.Person_Account_id = ba.Base_Account_id
                    WHERE pa.Person_Account_id = @AccountId;
                """,
                new{AccountId = accountId, 
                    Birthday = JsonSerializer.Serialize(pAccount.Birthday).Replace("\"", string.Empty)}
                );
    
            dbcontext.Close();
            return pAccount;

            //----------------------------------------------------------------------------------
            case BusinessAccount bAccount: 
                bAccount = await dbcontext.QuerySingleAsync<BusinessAccount>(
                """
                    INSERT INTO Business_Account (Business_Account_id, Cnpj)
                    VALUES (@AccountId, @CNPJ);

                    UPDATE Base_Account SET Advertisement_slots_amount = 1
                    WHERE Base_Account_id = @AccountId;  

                    SELECT busa.Cnpj, 
                           ba.Username, ba.Email, ba.UTC_datetime_creation, 
                           ba.Advertisement_slots_amount, ba.District_id
                    FROM Business_Account AS busa JOIN Base_Account AS ba ON busa.Business_Account_id = ba.Base_Account_id
                    WHERE busa.Business_Account_id = @AccountId;  
                """,
                new{AccountId = accountId, CNPJ = bAccount.CNPJ }
                );
            
            dbcontext.Close();
            return bAccount;
        }

        dbcontext.Close();
        throw new InvalidDataException("Object is neither Person nor Business Account");
    }
}

public interface IAccountSignInOutService
{
    public Task<BaseAccount> CreateAccountAsync(BaseAccount baseAccount);
    public string HashPassword(string unhashedPassword);
}