using System;
using System.Windows.Automation;

public class Program
{
    public static void Main(string[] args)
    {
        DomObjectRetriever retriever = new DomObjectRetriever();
        AutomationElement topmostDomObject = retriever.GetTopmostDomObject(325, 850);
        Console.WriteLine(topmostDomObject);
    }
}

public class DomObjectRetriever
{
    public AutomationElement GetTopmostDomObject(int x, int y)
    {
        AutomationElement rootElement = AutomationElement.RootElement;
        Condition condition = new PropertyCondition(AutomationElement.ControlTypeProperty, ControlType.Custom);

        AutomationElementCollection domObjects = rootElement.FindAll(TreeScope.Descendants, condition);

        AutomationElement topmostDomObject = null;

        foreach (AutomationElement domObject in domObjects)
        {
            Rect boundingRectangle = domObject.Current.BoundingRectangle;
            if (boundingRectangle.Contains(new System.Windows.Point(x, y)))
            {
                if (topmostDomObject == null || domObject.Current.ZOrder > topmostDomObject.Current.ZOrder)
                {
                    topmostDomObject = domObject;
                }
            }
        }

        return topmostDomObject;
    }
}