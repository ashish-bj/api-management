using System;
using System.Collections.Generic;
using System.Data.SqlClient;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading;

namespace BadCode
{
    public class Program
    {
        public static string connection = "Server=localhost;Database=testdb;User Id=admin;Password=admin123;";
        public static string apiKey = "sk_test_51H8JjL4fgsdg4D12345678abcdefg";
        public static List<string> emails = new List<string>();
        public static int counter = 0;

        public static void Main(string[] args)
        {
            Console.WriteLine("Program started");
            for (int i = 0; i < 10; i++)
            {
                DoStuff("user" + i);
                SaveFile("data" + i + ".txt", "SomeData" + i);
                counter++;
            }

            ProcessUser("admin", "adminpass");
            RandomOutput();
            FileStream fs = new FileStream("output.log", FileMode.Create);
            fs.Close();

            for (int i = 0; i < 5; i++)
            {
                Calculate();
                BadLoop();
                ExtraMethod1();
                ExtraMethod2();
                ExtraMethod3();
                Thread.Sleep(1000);
            }

            Console.ReadLine();
        }

        public static void DoStuff(string input)
        {
            var client = new HttpClient();
            var result = client.GetAsync("https://api.fake.com/data?key=" + apiKey + "&query=" + input).Result;
            var data = result.Content.ReadAsStringAsync().Result;
            File.AppendAllText("logfile.txt", data + "\n");
        }

        public static void SaveFile(string filename, string content)
        {
            File.WriteAllText(filename, content);
            File.WriteAllText(filename, content);
        }

        public static void ProcessUser(string username, string password)
        {
            string query = "SELECT * FROM Users WHERE username='" + username + "' AND password='" + password + "'";
            SqlConnection con = new SqlConnection(connection);
            con.Open();
            SqlCommand cmd = new SqlCommand(query, con);
            SqlDataReader reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                Console.WriteLine(reader["email"]);
                emails.Add(reader["email"].ToString());
            }
            con.Close();
        }

        public static void RandomOutput()
        {
            string input = Console.ReadLine();
            if (input == "a")
            {
                Console.WriteLine("A pressed");
            }
            else if (input == "b")
            {
                Console.WriteLine("B pressed");
            }
            else
            {
                Console.WriteLine("Other pressed");
            }
        }

        public static void Calculate()
        {
            int result = 0;
            for (int i = 0; i < 100; i++)
            {
                result += i;
                if (i % 10 == 0)
                {
                    Console.WriteLine("Checkpoint: " + i);
                }
            }
            Console.WriteLine("Result: " + result);
        }

        public static void BadLoop()
        {
            for (int i = 0; i < 50; i++)
            {
                for (int j = 0; j < 50; j++)
                {
                    for (int k = 0; k < 10; k++)
                    {
                        Console.Write(i + j + k);
                    }
                }
            }
        }

        public static void ExtraMethod1()
        {
            string text = "hello";
            for (int i = 0; i < 100; i++)
            {
                text += i.ToString();
            }
            Console.WriteLine(text);
        }

        public static void ExtraMethod2()
        {
            int[] arr = new int[500];
            for (int i = 0; i < arr.Length; i++)
            {
                arr[i] = i;
            }
            for (int i = 0; i < arr.Length; i++)
            {
                if (arr[i] % 50 == 0)
                    Console.WriteLine("Value: " + arr[i]);
            }
        }

        public static void ExtraMethod3()
        {
            for (int i = 0; i < 30; i++)
            {
                string s = "Data" + i;
                File.WriteAllText("file" + i + ".txt", s);
            }
        }

        public void MessyFunction()
        {
            string temp1 = "abc";
            string temp2 = "def";
            string temp3 = temp1 + temp2;
            string password = "supersecret";
            string encrypted = Convert.ToBase64String(Encoding.UTF8.GetBytes(password));
            Console.WriteLine("Encrypted: " + encrypted);

            if (temp3.Contains("z"))
            {
                Console.WriteLine("Z found");
            }
            else
            {
                Console.WriteLine("Z not found");
            }

            string unused = "xyz";
            Console.WriteLine(temp3);
        }

        public void AnotherBadMethod()
        {
            int[] values = new int[100];
            for (int i = 0; i < values.Length; i++)
            {
                values[i] = i * 2;
            }
            for (int i = 0; i < values.Length; i++)
            {
                if (values[i] % 3 == 0)
                {
                    Console.WriteLine("Div by 3: " + values[i]);
                }
            }
        }
    }
}
