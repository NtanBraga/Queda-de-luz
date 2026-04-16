public class Advertisement
{
    public int? Id;
	public bool ValidToBoost = false;
	public long UTC_LastEdit;
	public long UTC_BoostEndsAt;
    public string? RedirectLink;
	public Message? Message;

    //to recover from database
    public Advertisement(long Advertisement_id, bool Valid_to_boost, long UTC_last_edit, long UTC_boost_ends_at, string? Redirect_link)
    {
        this.Id = (int)Advertisement_id;
	    this.ValidToBoost = Valid_to_boost;
	    this.UTC_LastEdit = UTC_last_edit;
	    this.UTC_BoostEndsAt = UTC_boost_ends_at;
        this.RedirectLink = Redirect_link;
    }

    //to recover from database
    public Advertisement(Advertisement ad, Message message)
    {
        this.Id = (int)ad.Id!;
	    this.ValidToBoost = ad.ValidToBoost;
	    this.UTC_LastEdit = ad.UTC_LastEdit;
	    this.UTC_BoostEndsAt = ad.UTC_BoostEndsAt;
        this.RedirectLink = ad.RedirectLink;

        this.Message = message;
    }
	
}