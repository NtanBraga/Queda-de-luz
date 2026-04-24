public record PutEditAccountDataRequest(
    PutPersonDataSchema? person_Data,
    PutBusinessDataSchema? business_Data
);

public record PutPersonDataSchema(
    string  username,
    string  email,
    string? description,
    int     district_id,

    string? informal_work
);

public record PutBusinessDataSchema(
    string  username,
    string  email,
    string? description,
    int     district_id
);