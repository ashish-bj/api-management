using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;

namespace CleanCodeSample
{
    public class Program
    {
        public static async Task Main(string[] args)
        {
            Console.WriteLine("Application started.");
            var people = GenerateSamplePeople();
            var json = JsonSerializer.Serialize(people, new JsonSerializerOptions { WriteIndented = true });
            var filePath = Path.Combine(Directory.GetCurrentDirectory(), "people.json");

            await File.WriteAllTextAsync(filePath, json);
            Console.WriteLine($"Data saved to {filePath}");

            var readJson = await File.ReadAllTextAsync(filePath);
            var deserializedPeople = JsonSerializer.Deserialize<List<Person>>(readJson);

            Console.WriteLine("Loaded people from file:");
            foreach (var person in deserializedPeople!)
            {
                Console.WriteLine($"{person.FirstName} {person.LastName}, Age: {person.Age}, Email: {person.Email}");
            }
        }

        private static List<Person> GenerateSamplePeople()
        {
            var people = new List<Person>
            {
                new Person { FirstName = "Alice", LastName = "Johnson", Age = 30, Email = "alice@example.com" },
                new Person { FirstName = "Bob", LastName = "Smith", Age = 42, Email = "bob@example.com" },
                new Person { FirstName = "Charlie", LastName = "Brown", Age = 27, Email = "charlie@example.com" },
                new Person { FirstName = "Diana", LastName = "Prince", Age = 35, Email = "diana@example.com" },
                new Person { FirstName = "Eve", LastName = "Stone", Age = 23, Email = "eve@example.com" }
            };

            return people;
        }
    }

    public class Person
    {
        public string FirstName { get; set; } = string.Empty;
        public string LastName { get; set; } = string.Empty;
        public int Age { get; set; }
        public string Email { get; set; } = string.Empty;
    }
}        
