public static class AdvertisementMapping
{
    public static PostAdvertisementResponse ToPostAdvertisementResponse(this Advertisement ad)
    {
        return new PostAdvertisementResponse(
            ad_Id: (int)ad.Id!,
            valid_To_Boost: ad.ValidToBoost,
            ad_Text: ad.Message!.Text,
            image_Link: ad.Message.ImageLink,
            redirect_Link: ad.RedirectLink,
	        is_Hidden: ad.Message.IsHidden,
            utc_Last_Edit: ad.UTC_LastEdit,
            utc_Time_Created: (long)ad.Message.UTC_TimeSent!
        );
    }
}