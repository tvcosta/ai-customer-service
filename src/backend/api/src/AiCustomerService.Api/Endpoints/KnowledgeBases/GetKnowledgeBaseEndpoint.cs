namespace AiCustomerService.Api.Endpoints.KnowledgeBases;

using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Domain.Models;
using FastEndpoints;

public sealed class GetKnowledgeBaseEndpoint : EndpointWithoutRequest<KnowledgeBaseDto>
{
    private readonly ICoreApiClient _coreApi;

    public GetKnowledgeBaseEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Get("knowledge-bases/{id}");
        AllowAnonymous();
    }

    public override async Task HandleAsync(CancellationToken ct)
    {
        var id = Route<string>("id")!;
        var result = await _coreApi.GetKnowledgeBaseAsync(id, ct);
        await SendAsync(result, cancellation: ct);
    }
}
