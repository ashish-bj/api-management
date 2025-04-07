using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Hosting;
using System.Collections.Generic;
using System.Text.Json;

var app = WebApplication.Create();

// 🐛 In-memory storage, not thread-safe
List<User> users = new List<User>();

// ❌ No logging, no validation, hardcoded credentials
app.MapPost("/login", async (HttpContext context) =>
{
    var body = await JsonSerializer.DeserializeAsync<Dictionary<string, string>>(context.Request.Body);

    // 🛑 Hardcoded admin credentials
    if (body["username"] == "admin" && body["password"] == "admin123")
    {
        await context.Response.WriteAsync("Welcome, admin!");
    }
    else
    {
        context.Response.StatusCode = 401;
        await context.Response.WriteAsync("Invalid credentials");
    }
});

// ❌ No input validation, XSS possible
app.MapPost("/register", async (HttpContext context) =>
{
    var user = await JsonSerializer.DeserializeAsync<User>(context.Request.Body);
    users.Add(user);
    await context.Response.WriteAsync("User registered: " + user.Username);
});

// ❌ GET returns all users including passwords in plain text
app.MapGet("/users", async context =>
{
    await context.Response.WriteAsync(JsonSerializer.Serialize(users));
});

// 🤢 Global mutable static
static string ConnectionString = "Server=localhost;Database=
