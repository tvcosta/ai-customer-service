namespace AiCustomerService.Api.Endpoints.Health;

using AiCustomerService.Api.Application.Interfaces;
using FastEndpoints;

public sealed record HealthResponseDto(string Status, string CoreStatus);

public sealed class HealthEndpoint : EndpointWithoutRequest<HealthResponseDto>
{
    private readonly ICoreApiClient _coreApi;
    private readonly ILogger<HealthEndpoint> _logger;

    public HealthEndpoint(ICoreApiClient coreApi, ILogger<HealthEndpoint> logger)
    {
        _coreApi = coreApi;
        _logger = logger;
    }

    public override void Configure()
    {
        Get("health");
        AllowAnonymous();
    }

    public override async Task HandleAsync(CancellationToken ct)
    {
        var coreStatus = "unreachable";

        try
        {
            using var timeoutCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
            timeoutCts.CancelAfter(TimeSpan.FromSeconds(5));

            var coreHealthy = await _coreApi.CheckHealthAsync(timeoutCts.Token);
            coreStatus = coreHealthy ? "healthy" : "unreachable";
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Core API health check failed");
        }

        await SendAsync(new HealthResponseDto("healthy", coreStatus), cancellation: ct);
    }
}
