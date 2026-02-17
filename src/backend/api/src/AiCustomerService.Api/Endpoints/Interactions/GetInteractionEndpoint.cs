namespace AiCustomerService.Api.Endpoints.Interactions;

using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Domain.Models;
using FastEndpoints;

public sealed class GetInteractionEndpoint : EndpointWithoutRequest<InteractionDto>
{
    private readonly ICoreApiClient _coreApi;

    public GetInteractionEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Get("interactions/{id}");
        AllowAnonymous();
    }

    public override async Task HandleAsync(CancellationToken ct)
    {
        var id = Route<string>("id")!;
        var result = await _coreApi.GetInteractionAsync(id, ct);
        await SendAsync(result, cancellation: ct);
    }
}
