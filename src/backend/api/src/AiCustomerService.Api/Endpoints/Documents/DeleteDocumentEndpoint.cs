namespace AiCustomerService.Api.Endpoints.Documents;

using AiCustomerService.Api.Application.Interfaces;
using FastEndpoints;

public sealed class DeleteDocumentEndpoint : EndpointWithoutRequest
{
    private readonly ICoreApiClient _coreApi;

    public DeleteDocumentEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Delete("knowledge-bases/{kbId}/documents/{docId}");
        AllowAnonymous();
    }

    public override async Task HandleAsync(CancellationToken ct)
    {
        var kbId = Route<string>("kbId")!;
        var docId = Route<string>("docId")!;
        await _coreApi.DeleteDocumentAsync(kbId, docId, ct);
        await SendNoContentAsync(cancellation: ct);
    }
}
