using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Application.Services;
using AiCustomerService.Api.Infrastructure.Middleware;
using AiCustomerService.Api.Infrastructure.Telemetry;
using FastEndpoints;
using FastEndpoints.Swagger;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddFastEndpoints();
builder.Services.SwaggerDocument(o =>
{
    o.DocumentSettings = s =>
    {
        s.Title = "AI Customer Service - Backend API";
        s.Version = "v1";
        s.Description = "Public gateway API for AI Customer Service system";
    };
});

// CORS configuration
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins("http://localhost:3000")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

// HttpClient for Core API
var coreApiConfig = builder.Configuration.GetSection("CoreApi");
builder.Services.AddHttpClient<ICoreApiClient, CoreApiClient>(client =>
{
    var baseUrl = coreApiConfig.GetValue<string>("BaseUrl") ?? "http://localhost:8000";
    var timeoutSeconds = coreApiConfig.GetValue<int>("TimeoutSeconds", 30);

    client.BaseAddress = new Uri(baseUrl);
    client.Timeout = TimeSpan.FromSeconds(timeoutSeconds);
});

// OpenTelemetry setup
TelemetrySetup.ConfigureOpenTelemetry(builder.Services, builder.Configuration);

// Health checks are handled by the FastEndpoints HealthEndpoint

var app = builder.Build();

// Configure the HTTP request pipeline
app.UseCors();

app.UseMiddleware<ErrorHandlingMiddleware>();

app.UseFastEndpoints(c =>
{
    c.Endpoints.RoutePrefix = "api/v1";
});

if (app.Environment.IsDevelopment())
{
    app.UseSwaggerGen();
}

app.Run("http://0.0.0.0:5000");

// Expose Program class for WebApplicationFactory in integration tests
public partial class Program { }
