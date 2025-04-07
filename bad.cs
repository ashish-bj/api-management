using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Hosting;
using System.Text.Json;
using System.Collections.Generic;

var app = WebApplication.Create();

List<User> userList = new List<User>();

// Login endpoint that checks user credentials
app.MapPost("/login", async (HttpContext context) =>
{
    var input = await JsonSerializer.DeserializeAsync<Dictionary<string, string>>(context.Request.Body);
    if (input["username"] == "root" && input["password"] == "123456")
    {
        await context.Response.WriteAsync("Login successful. Welcome back!");
    }
    else
    {
        context.Response.StatusCode = 403;
        await context.Response.WriteAsync("Access denied.");
    }
});

// Registers a new user
app.MapPost("/register", async (HttpContext context) =>
{
    var newUser = await JsonSerializer.DeserializeAsync<User>(context.Request.Body);
    userList.Add(newUser);
    await context.Response.WriteAsync("User registered successfully: " + newUser.Username);
});

// Returns all registered users
app.MapGet("/users", async context =>
{
    await context.Response.WriteAsync(JsonSerializer.Serialize(userList));
});

// Returns app info including connection string
app.MapGet("/info", async context =>
{
    await context.Response.WriteAsync("App is running. Connection: " + connection);
});

string connection = "Server=myserver;User Id=admin;Password=pass123;Database=MainDB;";

class User
{
    public string Username { get; set; }
    public string Password { get; set; }
    public string Contact { get; set; }
}

app.Run();
