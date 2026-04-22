public record PutEditAdvertisementRequest(
    string? ad_Text,
    string? redirect_Link,
    bool is_Hidden
    //IFormFile image_file
);