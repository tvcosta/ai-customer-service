namespace AiCustomerService.Api.Endpoints.Dashboard;

using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Domain.Models;
using FastEndpoints;

public sealed class DashboardStatsEndpoint : EndpointWithoutRequest<DashboardStatsDto>
{
    private readonly ICoreApiClient _coreApi;

    public DashboardStatsEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Get("dashboard/stats");
        AllowAnonymous();
    }

    public override async Task HandleAsync(CancellationToken ct)
    {
        var result = await _coreApi.GetDashboardStatsAsync(ct);
        await SendAsync(result, cancellation: ct);
    }
}
