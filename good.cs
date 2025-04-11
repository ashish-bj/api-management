using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Data.SqlClient;

namespace GoodCode
{
    public class Program
    {
        private static readonly string ConnectionString = Environment.GetEnvironmentVariable("DB_CONNECTION") ?? "";
        private static readonly string ApiKey = Environment.GetEnvironmentVariable("API_KEY") ?? "";

        public static async Task Main(string[] args)
        {
            Console.WriteLine("Program started");
            var usernames = GenerateUsernames(50);

            var results = await FetchDataFromApiAsync(usernames);
            await SaveToFilesAsync(results);

            var emails = await GetUserEmailsAsync("admin", "adminpass");
            Console.WriteLine($"Fetched {emails.Count} emails.");

            var outputFile = "output.log";
            await File.WriteAllTextAsync(outputFile, string.Join("\n", emails));

            await ExecuteAdditionalTasks();
        }

        private static List<string> GenerateUsernames(int count)
        {
            var list = new List<string>();
            for (int i = 0; i < count; i++)
            {
                list.Add($"user{i}");
            }
            return list;
        }

        private static async Task<List<string>> FetchDataFromApiAsync(List<string> usernames)
        {
            var client = new HttpClient();
            var results = new List<string>();

            foreach (var user in usernames)
            {
                var response = await client.GetAsync($"https://api.fake.com/data?key={ApiKey}&query={user}");
                if (response.IsSuccessStatusCode)
                {
                    var data = await response.Content.ReadAsStringAsync();
                    results.Add(data);
                }
            }

            return results;
        }

        private static async Task SaveToFilesAsync(List<string> contents)
        {
            for (int i = 0; i < contents.Count; i++)
            {
                var filename = $"data_{i}.txt";
                await File.WriteAllTextAsync(filename, contents[i]);
            }
        }

        private static async Task<List<string>> GetUserEmailsAsync(string username, string password)
        {
            var emails = new List<string>();

            var query = "SELECT email FROM Users WHERE username=@username AND password=@password";
            await using var connection = new SqlConnection(ConnectionString);
            await connection.OpenAsync();

            await using var command = new SqlCommand(query, connection);
            command.Parameters.AddWithValue("@username", username);
            command.Parameters.AddWithValue("@password", password);

            await using var reader = await command.ExecuteReaderAsync();
            while (await reader.ReadAsync())
            {
                emails.Add(reader.GetString(0));
            }

            return emails;
        }

        private static async Task ExecuteAdditionalTasks()
        {
            await Task.WhenAll(
                Task.Run(() => ProcessBatch("Task1")),
                Task.Run(() => ProcessBatch("Task2")),
                Task.Run(() => ProcessBatch("Task3")),
                Task.Run(() => ProcessBatch("Task4"))
            );

            for (int i = 0; i < 10; i++)
            {
                await ProcessNumbersAsync(i);
            }

            await LogJsonData();
        }

        private static void ProcessBatch(string name)
        {
            for (int i = 0; i < 100; i++)
            {
                Console.WriteLine($"{name}: Processing item {i}");
            }
        }

        private static async Task ProcessNumbersAsync(int index)
        {
            await Task.Delay(100);
            Console.WriteLine($"Processed number {index}");

            var path = Path.Combine("numbers", $"num_{index}.txt");
            Directory.CreateDirectory("numbers");
            await File.WriteAllTextAsync(path, index.ToString());
        }

        private static async Task LogJsonData()
        {
            var data = new List<SampleData>();
            for (int i = 0; i < 100; i++)
            {
                data.Add(new SampleData { Id = i, Name = $"Name{i}", Timestamp = DateTime.UtcNow });
            }

            var json = JsonSerializer.Serialize(data);
            await File.WriteAllTextAsync("data.json", json);
        }
    }

    public class SampleData
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public DateTime Timestamp { get; set; }
    }
}        
