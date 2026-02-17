namespace AiCustomerService.Api.Endpoints.Interactions;

using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Domain.Models;
using FastEndpoints;

public sealed class ListInteractionsEndpoint : EndpointWithoutRequest<List<InteractionDto>>
{
    private readonly ICoreApiClient _coreApi;

    public ListInteractionsEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Get("interactions");
        AllowAnonymous();
    }

    public override async Task HandleAsync(CancellationToken ct)
    {
        var result = await _coreApi.ListInteractionsAsync(ct);
        await SendAsync(result, cancellation: ct);
    }
}
