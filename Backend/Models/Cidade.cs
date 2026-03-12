public class Cidade
{
    public int Id {get; private set;} = -1 ;
    public string Nome {get; private set;}
    public string EstadoSigla {get; private set;}

    public Cidade(int id, string nome, string estadoSigla)
    {
        this.Id = id;
        this.Nome = nome;
        this.EstadoSigla = estadoSigla;
    }

    public Cidade(string nome, string estadoSigla)
    {
        this.Nome = nome;
        this.EstadoSigla = estadoSigla;
    }
}