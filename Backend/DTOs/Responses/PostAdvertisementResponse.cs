public record PostAdvertisementResponse(
    int ad_Id,
    bool valid_To_Boost,

    string ad_Text,
    string? image_Link,
    string? redirect_Link,
	bool is_Hidden,

    long utc_Last_Edit,
    long utc_Time_Created
);