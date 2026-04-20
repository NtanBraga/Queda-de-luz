public  class AdPageValidator
{
    private IBlackoutMapConnectionFactory _connectionFactory;
    public AdPageValidator(IBlackoutMapConnectionFactory connectionFactory)
    {
        this._connectionFactory = connectionFactory;
    }

    public async Task<(bool, RequestError?)> IsValid(GetActiveAdsRequest_QueryParams requestParams)
    {
        RequestError? error = null;

        if(requestParams.district_Id is null)
        {
            error = new RequestError(
                StatusCodes.Status400BadRequest,
                "district_Id query Param cannot be Null"
            );
            return (false, error);
        }

        // if(requestParams.district_Id is null)
        // {
        //     error = new RequestError(
        //         StatusCodes.Status404NotFound,
        //         $"district [{requestParams.district_Id}] Not Found"
        //     );
        //     return (false, error);
        // }

        return (true, null);
    } 
}