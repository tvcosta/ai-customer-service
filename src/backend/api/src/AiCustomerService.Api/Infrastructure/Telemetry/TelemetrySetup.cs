namespace AiCustomerService.Api.Infrastructure.Telemetry;

using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

public static class TelemetrySetup
{
    public static void ConfigureOpenTelemetry(IServiceCollection services, IConfiguration configuration)
    {
        var serviceName = configuration.GetValue<string>("OpenTelemetry:ServiceName") ?? "ai-customer-service-api";
        var otlpEndpoint = configuration.GetValue<string>("OpenTelemetry:Endpoint") ?? "http://localhost:4317";

        services.AddOpenTelemetry()
            .ConfigureResource(resource => resource.AddService(serviceName))
            .WithTracing(tracing => tracing
                .AddAspNetCoreInstrumentation()
                .AddHttpClientInstrumentation()
                .AddOtlpExporter(opts => opts.Endpoint = new Uri(otlpEndpoint)));
    }
}
