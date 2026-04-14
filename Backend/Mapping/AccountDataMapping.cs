public static  class AccountDataMapping
{
    public static PersonAccountData ToPersonAccountData(this PersonAccount account, string districtName, bool includePrivateData)
    {
        Public_PersonAccountData publicData = new Public_PersonAccountData(
            username: account.Username,
            email: account.Email,
            description: account.Description ?? string.Empty,
            profile_Picture_Link: account.ProfilePictureLink,
            district_Id: account.DistrictId,
            district_Name: districtName,
            Visible_Ads:  new(),

            Birthday: account.Birthday
        );

        Private_PersonAccountData? privateData = null;
        if(includePrivateData == true)
        {
            privateData = new Private_PersonAccountData(
                advertisement_Slots_Amount: account.AdvertisementSlotsAmount,
                Hidden_Ads: new()
            );
        }

        return new PersonAccountData(
            publicData,
            privateData
        );
    }
}