namespace AiCustomerService.Api.Endpoints.Documents;

using AiCustomerService.Api.Application.Interfaces;
using FastEndpoints;

public sealed class TriggerIndexingEndpoint : EndpointWithoutRequest
{
    private readonly ICoreApiClient _coreApi;

    public TriggerIndexingEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Post("knowledge-bases/{kbId}/index");
        AllowAnonymous();
    }

    public override async Task HandleAsync(CancellationToken ct)
    {
        var kbId = Route<string>("kbId")!;
        await _coreApi.TriggerIndexingAsync(kbId, ct);
        await SendOkAsync(cancellation: ct);
    }
}
