namespace AiCustomerService.Api.Endpoints.Query;

using System.Diagnostics;
using AiCustomerService.Api.Application.Interfaces;
using AiCustomerService.Api.Domain.Models;
using AiCustomerService.Api.Infrastructure.Telemetry;
using FastEndpoints;

public sealed class QueryEndpoint : Endpoint<QueryRequestDto, QueryResponseDto>
{
    private readonly ICoreApiClient _coreApi;

    public QueryEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Post("query");
        AllowAnonymous();
    }

    public override async Task HandleAsync(QueryRequestDto req, CancellationToken ct)
    {
        using var activity = TelemetrySetup.ActivitySource.StartActivity("proxy.query", ActivityKind.Client);
        activity?.SetTag("query.kb_id", req.KnowledgeBaseId);

        var result = await _coreApi.QueryAsync(req, ct);

        activity?.SetTag("interaction.id", result.InteractionId);

        await SendAsync(result, cancellation: ct);
    }
}
