using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System.ComponentModel.DataAnnotations;

var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddSingleton<ITaskRepository, InMemoryTaskRepository>();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Swagger for testing
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.MapPost("/tasks", async (TaskDto input, ITaskRepository repo, ILogger<Program> logger) =>
{
    var context = new ValidationContext(input, serviceProvider: null, items: null);
    var results = new List<ValidationResult>();
    if (!Validator.TryValidateObject(input, context, results, true))
    {
        return Results.ValidationProblem(results.ToDictionary(r => r.MemberNames.First(), r => new[] { r.ErrorMessage ?? "Invalid input" }));
    }

    var task = new TaskModel
    {
        Id = Guid.NewGuid(),
        Title = input.Title,
        Description = input.Description,
        CreatedAt = DateTime.UtcNow,
        IsCompleted = false
    };

    await repo.AddTaskAsync(task);
    logger.LogInformation("Task added with ID {TaskId}", task.Id);

    return Results.Created($"/tasks/{task.Id}", task);
});

app.MapGet("/tasks", async (ITaskRepository repo) =>
{
    var tasks = await repo.GetTasksAsync();
    return Results.Ok(tasks);
});

app.Run();

// DTOs & Models
record TaskDto([Required]string Title, string? Description);

class TaskModel
{
    public Guid Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string? Description { get; set; }
    public DateTime CreatedAt { get; set; }
    public bool IsCompleted { get; set; }
}

// Repository
interface ITaskRepository
{
    Task AddTaskAsync(TaskModel task);
    Task<IEnumerable<TaskModel>> GetTasksAsync();
}

class InMemoryTaskRepository : ITaskRepository
{
    private readonly List<TaskModel> _tasks = [];

    public Task AddTaskAsync(TaskModel task)
    {
        _tasks.Add(task);
        return Task.CompletedTask;
    }

    public Task<IEnumerable<TaskModel>> GetTasksAsync()
    {
        return Task.FromResult<IEnumerable<TaskModel>>(_tasks);
    }
}
