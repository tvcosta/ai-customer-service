namespace AiCustomerService.Api.Infrastructure.Telemetry;

using System.Diagnostics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

public static class TelemetrySetup
{
    public const string ActivitySourceName = "AiCustomerService.Api";

    public static readonly ActivitySource ActivitySource = new(ActivitySourceName);

    public static void ConfigureOpenTelemetry(IServiceCollection services, IConfiguration configuration)
    {
        var serviceName = configuration.GetValue<string>("OpenTelemetry:ServiceName") ?? "ai-customer-service-api";
        var otlpEndpoint = configuration.GetValue<string>("OpenTelemetry:Endpoint") ?? "http://localhost:4317";

        services.AddOpenTelemetry()
            .ConfigureResource(resource => resource.AddService(serviceName))
            .WithTracing(tracing => tracing
                .AddSource(ActivitySourceName)
                .AddAspNetCoreInstrumentation()
                .AddHttpClientInstrumentation()
                .AddOtlpExporter(opts => opts.Endpoint = new Uri(otlpEndpoint)));
    }
}
