public  class AccountSignInOutValidator
{
    private IBlackoutMapConnectionFactory _connectionFactory;

    public AccountSignInOutValidator(IBlackoutMapConnectionFactory connectionFactory)
    {
        this._connectionFactory = connectionFactory;
    }

    public (bool, RequestError?) IsValid(PostAccountRequest request)
    {
        RequestError? error = null;

        if(request.Person_Details is not null && request.Business_Details is not null ||
           request.Person_Details is null     && request.Business_Details is null)
        {
            error = new RequestError(StatusCodes.Status400BadRequest, "Either PersonDetails or BusinessDetails should be not null");
            return (false, error);
        }

        //<<TODO: validate Email>>
        //<<TODO: validate District Id Existence>>
        //<<TODO: validate duplicate Username>>

        return (true, error);
    }
}