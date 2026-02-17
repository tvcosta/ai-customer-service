namespace AiCustomerService.Api.Endpoints.KnowledgeBases;

using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Domain.Models;
using FastEndpoints;

public sealed class ListKnowledgeBasesEndpoint : EndpointWithoutRequest<List<KnowledgeBaseDto>>
{
    private readonly ICoreApiClient _coreApi;

    public ListKnowledgeBasesEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Get("knowledge-bases");
        AllowAnonymous();
    }

    public override async Task HandleAsync(CancellationToken ct)
    {
        var result = await _coreApi.ListKnowledgeBasesAsync(ct);
        await SendAsync(result, cancellation: ct);
    }
}
