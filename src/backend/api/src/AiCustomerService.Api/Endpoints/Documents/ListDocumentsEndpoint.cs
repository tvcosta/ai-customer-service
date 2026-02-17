namespace AiCustomerService.Api.Endpoints.Documents;

using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Domain.Models;
using FastEndpoints;

public sealed class ListDocumentsEndpoint : EndpointWithoutRequest<List<DocumentDto>>
{
    private readonly ICoreApiClient _coreApi;

    public ListDocumentsEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Get("knowledge-bases/{kbId}/documents");
        AllowAnonymous();
    }

    public override async Task HandleAsync(CancellationToken ct)
    {
        var kbId = Route<string>("kbId")!;
        var result = await _coreApi.ListDocumentsAsync(kbId, ct);
        await SendAsync(result, cancellation: ct);
    }
}
