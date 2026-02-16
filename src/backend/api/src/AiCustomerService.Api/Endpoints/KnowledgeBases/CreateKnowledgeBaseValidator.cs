namespace AiCustomerService.Api.Endpoints.KnowledgeBases;

using AiCustomerService.Api.Domain.Models;
using FastEndpoints;
using FluentValidation;

public sealed class CreateKnowledgeBaseValidator : Validator<CreateKnowledgeBaseRequestDto>
{
    public CreateKnowledgeBaseValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Name is required")
            .MaximumLength(200).WithMessage("Name must not exceed 200 characters");
    }
}
