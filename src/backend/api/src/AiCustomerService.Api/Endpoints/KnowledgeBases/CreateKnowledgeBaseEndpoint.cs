namespace AiCustomerService.Api.Endpoints.KnowledgeBases;

using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Domain.Models;
using FastEndpoints;

public sealed class CreateKnowledgeBaseEndpoint : Endpoint<CreateKnowledgeBaseRequestDto, KnowledgeBaseDto>
{
    private readonly ICoreApiClient _coreApi;

    public CreateKnowledgeBaseEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Post("knowledge-bases");
        AllowAnonymous();
    }

    public override async Task HandleAsync(CreateKnowledgeBaseRequestDto req, CancellationToken ct)
    {
        var result = await _coreApi.CreateKnowledgeBaseAsync(req, ct);
        await SendCreatedAtAsync<GetKnowledgeBaseEndpoint>(new { id = result.Id }, result, cancellation: ct);
    }
}
