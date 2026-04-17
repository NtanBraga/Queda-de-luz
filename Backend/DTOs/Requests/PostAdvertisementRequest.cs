public record PostAdvertisementRequest(
    string? ad_Text,
    string? redirect_Link,
    bool? is_Hidden = true
    //IFormFile image_file
);