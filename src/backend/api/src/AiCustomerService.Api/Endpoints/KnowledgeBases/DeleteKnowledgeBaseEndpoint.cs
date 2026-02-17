namespace AiCustomerService.Api.Endpoints.KnowledgeBases;

using AiCustomerService.Api.Application.Interfaces;
using FastEndpoints;

public sealed class DeleteKnowledgeBaseEndpoint : EndpointWithoutRequest
{
    private readonly ICoreApiClient _coreApi;

    public DeleteKnowledgeBaseEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Delete("knowledge-bases/{id}");
        AllowAnonymous();
    }

    public override async Task HandleAsync(CancellationToken ct)
    {
        var id = Route<string>("id")!;
        await _coreApi.DeleteKnowledgeBaseAsync(id, ct);
        await SendNoContentAsync(cancellation: ct);
    }
}
