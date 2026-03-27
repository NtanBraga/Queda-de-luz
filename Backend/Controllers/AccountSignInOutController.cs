using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("accounts")]
public class AccountSignInOutController : ControllerBase
{
    private IAccountSignInOutService _accountService;
    private AccountSignInOutValidator _validator;

    public AccountSignInOutController(IAccountSignInOutService service, AccountSignInOutValidator validator)
    {
        this._accountService = service;
        this._validator = validator;
    } 

    [HttpPost]
    public async Task<IActionResult> PostAccountAsync(PostAccountRequest request)
    {
        (bool isValid, var error)= this._validator.IsValid(request);
        if(isValid == false)
        { 
            return this.StatusCode(error!.StatusCode, error.Message); 
        }

        string hashedPassword = this._accountService.HashPassword(request.Unhashed_Password);
        
        BaseAccount account;
        if(request.Person_Details is not null){
            account = request.ToPersonAccount(hashedPassword);
        }
        else{
            account = request.ToBusinessAccount(hashedPassword);
        }
    
        BaseAccount createdAccount = await this._accountService.CreateAccountAsync(account);
        PostAccountResponse response = createdAccount.ToPostAccountResponse();

        return Ok(response);
        //return Created();
    }

}