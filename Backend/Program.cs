var builder = WebApplication.CreateBuilder(args);

//builder.Services.AddOpenApi();
builder.Services.AddControllers();

//builder.Services.AddScoped<>()

//To Avoid Wasting Time for a prototype
const string AllowAllPolicyName = "AllowAll";
builder.Services.AddCors(options =>
{
    options.AddPolicy(AllowAllPolicyName, policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

//Database Configs
const string DatabaseDirectory = @".\Database\";
const string DatabaseFile = @"BlackoutMap.db";
if (!Directory.Exists(DatabaseDirectory) || !File.Exists(DatabaseDirectory + DatabaseFile))
{
    Directory.CreateDirectory(DatabaseDirectory);
    File.Create(DatabaseDirectory + DatabaseFile).Close();
}

// builder.Services.AddDbContext<ClassNameContext>(options =>
// {
//     const string connectionString = @"Data Source=.\Database\BlackoutMap.db;";
//     options.UseSqlite(connectionString);
// });

var app = builder.Build();

// using (IServiceScope scope = app.Services.CreateScope())
// {
//     ClassNameContext dbContext = scope.ServiceProvider.GetRequiredService<ClassNameContext>();
//     dbContext.Database.EnsureCreated();
// }

// Configure the HTTP request pipeline.
//if (app.Environment.IsDevelopment()){ app.MapOpenApi(); }
//app.UseHttpsRedirection();

app.UseCors(AllowAllPolicyName);
app.MapControllers();

app.Run();
